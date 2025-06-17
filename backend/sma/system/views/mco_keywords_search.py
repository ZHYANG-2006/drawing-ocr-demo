from django.db import connection
import os
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.decorators import action
from django.http import FileResponse, JsonResponse
from application import settings
from sma.system.models.mco import MCOPdfFile, MCOJsonFile, MCOJsonPage, MCOJsonContent, MCOJsonParagraph
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet
import cx_Oracle

class MCOParagraphSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = MCOJsonParagraph
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

class MCOParagraphViewSet(CustomModelViewSet):
    """
    PdfFile 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = MCOJsonParagraph.objects.all()
    serializer_class = MCOParagraphSerializer

    create_serializer_class = MCOParagraphSerializer
    update_serializer_class = MCOParagraphSerializer

    search_fields = [
        'value',
        'keywords',
        'creator_name',
        'create_datetime',
        'creator',
        'uploader_name',
    ]

    ordering_fields = [
        'creator_name',
        'create_datetime',
        'creator',
        'uploader_name',
    ]

    def list(self, request, *args, **kwargs):
        """
        重写list方法
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset()).order_by('-create_datetime')
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(serializer.data, msg="获取成功")

    @action(detail=False, methods=['post'])
    def getpdf(self, request):
        """
        获取 PDF 文件，用于在线预览 (inline)
        """
        try:
            file_id = request.data.get("id")
            if not file_id:
                return ErrorResponse(msg="缺少审核版本 ID")
            pdf_file = MCOPdfFile.objects.get(id=file_id)
            if not pdf_file:
                return ErrorResponse(msg="未找到对应的PDF文件")
            pdf_file_path = pdf_file.file_path
            if not pdf_file_path:
                return ErrorResponse(msg="PDF 文件路径为空")

            response = FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
            # inline: 浏览器内联预览
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(pdf_file_path)}"'
            return response
        except MCOPdfFile.DoesNotExist:
            return ErrorResponse(msg="指定的PDF不存在")
        except Exception as e:
            return ErrorResponse(msg=f"获取 PDF 文件失败: {str(e)}")

    @action(detail=False, methods=['post'])
    def download_pdf(self, request):
        """
        根据 pdf_id 下载对应的 PDF 文件
        """
        try:
            pdf_id = request.data.get("pdf_id")
            if not pdf_id:
                return ErrorResponse(msg="缺少 PDF ID 参数")
            pdf_file = MCOPdfFile.objects.get(id=pdf_id)
            if not pdf_file:
                return ErrorResponse(msg="未找到对应的PDF文件")
            pdf_file_path = pdf_file.file_path
            if not pdf_file_path or not os.path.exists(pdf_file_path):
                return ErrorResponse(msg="PDF 文件路径为空或文件不存在")

            response = FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
            # attachment: 触发下载
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_file_path)}"'
            return response
        except MCOPdfFile.DoesNotExist:
            return ErrorResponse(msg="指定的PDF不存在")
        except Exception as e:
            return ErrorResponse(msg=f"下载 PDF 文件失败: {str(e)}")

    @action(detail=False, methods=['post'])
    def search_paragraphs(self, request):
        query = request.data.get('query', '')
        page = int(request.data.get('page', 1) or 1)
        page_size = int(request.data.get('page_size', 10) or 10)
        offset = (page - 1) * page_size
        # 1. 将 query 拆分成多关键词，过滤掉空值
        keywords = [kw for kw in query.split() if kw]

        # 如果没有输入任何关键字，也不想过滤，就用 1=1
        # 否则就对每个关键词生成: LOWER(value) LIKE LOWER(:kw0)
        count_conditions = []
        data_conditions = []
        params = {}

        if keywords:
            for i, kw in enumerate(keywords):
                # 比如 kw0, kw1, kw2...
                key = f'kw{i}'
                # LIKE '%keyword%'
                params[key] = f'%{kw}%'
                # condition = (f"(LOWER(value) LIKE LOWER(:{key}) or "
                #              f"(LOWER(DRAWING_NUMBER) LIKE LOWER(:{key}) or"
                #              f"(LOWER(PDF_NAME) LIKE LOWER(:{key}) or"
                #              f"(LOWER(TITLE) LIKE LOWER(:{key}) or"
                #              f"(LOWER(REV) = LOWER(:{key}) or"
                #              f"(NUM) = LOWER(:{key}) or")
                condition = f"""
                    (
                        LOWER(value) LIKE LOWER(:{key})
                        OR LOWER(drawing_number) LIKE LOWER(:{key})
                        OR LOWER(pdf_name) LIKE LOWER(:{key})
                        OR LOWER(title) LIKE LOWER(:{key})
                        OR LOWER(internal_code) LIKE LOWER(:{key})
                        OR LOWER(project_description) LIKE LOWER(:{key})
                        OR LOWER(flex_part_number) LIKE LOWER(:{key})
                        OR TO_CHAR(num) = :{key}
                        OR TO_CHAR(create_datetime, 'YYYY-MM-DD HH24:MI:SS') LIKE :{key}
                    )
                """
                count_conditions.append(condition)
                data_conditions.append(condition)

            count_where_clause = " AND ".join(count_conditions)
            data_where_clause = " AND ".join(data_conditions)
        else:
            # 用户没输入任何关键词 => 不做过滤
            count_where_clause = "1=1"
            data_where_clause = "1=1"

        # 2. 拼接出 COUNT SQL
        count_sql = f"""
        WITH base AS (
            SELECT
                drawing_number,
                rev,
                CASE
                  WHEN REGEXP_LIKE(rev, '^\\d+$')
                    THEN TO_NUMBER(rev)
                  WHEN REGEXP_LIKE(rev, '^[A-Z]$')
                    THEN 100 + ASCII(UPPER(rev)) - ASCII('A')
                  ELSE 999
                END AS rev_sort
            FROM SMA_MCO_PARAGRAPH
            WHERE {count_where_clause}
        ),
        ranked AS (
            SELECT
                drawing_number,
                rev_sort,
                DENSE_RANK() OVER (
                    PARTITION BY drawing_number
                    ORDER BY rev_sort DESC
                ) AS rk
            FROM base
        )
        SELECT COUNT(1)
        FROM ranked
        WHERE rk = 1
        """

        # 3. 执行 COUNT 查询
        with connection.cursor() as cursor:
            cursor.execute(count_sql, params)  # 注意，这里使用 params
            total_count = cursor.fetchone()[0]

        # 4. 再构造分页查询
        #    这里可以保留你原来的 score 计算，或做简化
        sql = f"""
                WITH base AS (
                    SELECT
                        id,
                        DBMS_LOB.SUBSTR(
                          value,
                          CASE
                            WHEN DBMS_LOB.GETLENGTH(value) < 2000 THEN DBMS_LOB.GETLENGTH(value)
                            ELSE 2000
                          END,
                          1
                        ) AS value_str,
                        pdf_id,
                        pdf_name,
                        title,
                        drawing_number,
                        rev,
                        internal_code,
                        project_description,
                        flex_part_number,
                        num,
                        create_datetime,
                        CASE
                          WHEN REGEXP_LIKE(rev, '^\d+$')
                            THEN TO_NUMBER(rev)
                          WHEN REGEXP_LIKE(rev, '^[A-Z]$')
                            THEN 100 + ASCII(UPPER(rev)) - ASCII('A')
                          ELSE 999
                        END AS rev_sort
                    FROM SMA_MCO_PARAGRAPH
                    WHERE {data_where_clause}
                ),
                ranked AS (
                    SELECT
                        base.*,
                        DENSE_RANK() OVER (
                            PARTITION BY drawing_number
                            ORDER BY rev_sort DESC
                        ) AS rk
                    FROM base
                )
                SELECT
                    id, value_str, pdf_id, pdf_name, title,
                    drawing_number, rev, internal_code,
                    project_description, flex_part_number,
                    num, create_datetime
                FROM ranked
                WHERE rk = 1                               -- 取并列第一的所有行
                ORDER BY create_datetime DESC
                OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY

            """

        # 分页相关的参数，也要一并传入
        params['offset'] = offset
        params['limit'] = page_size

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            para_id, text, pdf_id, pdf_name, title, drawing_number, rev, internal_code, project_description, flex_part_number, num, create_datetime = row
            results.append({
                "paragraph_id": para_id,
                "text": text,
                "pdf_id": pdf_id,
                # "score": score,
                "pdf_name": f"{pdf_name}.pdf",
                "title": title,
                "drawing_number": drawing_number,
                "rev": rev,
                "internal_code": internal_code,
                "project_description": project_description,
                "flex_part_number": flex_part_number,
                "num": num,
                "create_datetime": create_datetime,
                "pdf_url": f"/media/pdfs/{pdf_id}.pdf"
            })

        response_data = {
            "query": query,
            "page": page,
            "page_size": page_size,
            "results": results,
            "total_results": total_count,
        }
        return SuccessResponse(response_data)

    @action(detail=False, methods=['post'])
    def search_paragraphs_filter(self, request):
        # 1. 拆关键词 & 构造绑定变量
        query = request.data.get('query', '') or ''
        keywords = [kw for kw in query.split() if kw]
        params = {}
        conditions = []

        if keywords:
            for i, kw in enumerate(keywords):
                key = f'kw{i}'
                params[key] = f'%{kw}%'
                conditions.append(f"""
                  (
                    LOWER(value) LIKE LOWER(:{key})
                    OR LOWER(drawing_number) LIKE LOWER(:{key})
                    OR LOWER(pdf_name) LIKE LOWER(:{key})
                    OR LOWER(title) LIKE LOWER(:{key})
                    OR LOWER(internal_code) LIKE LOWER(:{key})
                    OR LOWER(project_description) LIKE LOWER(:{key})
                    OR LOWER(flex_part_number) LIKE LOWER(:{key})
                    OR TO_CHAR(num) = :{key}
                    OR TO_CHAR(create_datetime, 'YYYY-MM-DD HH24:MI:SS') LIKE :{key}
                  )
                """)
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 2. 一次性查询所有最新 rev 的记录（去掉分页）
        sql = f"""
          WITH base AS (
            SELECT
              id,
              DBMS_LOB.SUBSTR(
                  value,
                  CASE
                    WHEN DBMS_LOB.GETLENGTH(value) < 2000 THEN DBMS_LOB.GETLENGTH(value)
                    ELSE 2000
                  END,
                  1
                ) AS value_str,
              pdf_id,
              pdf_name,
              title,
              drawing_number,
              rev,
              internal_code,
              project_description,
              flex_part_number,
              num,
              create_datetime,
              CASE
                WHEN REGEXP_LIKE(rev, '^\d+$') THEN TO_NUMBER(rev)
                WHEN REGEXP_LIKE(rev, '^[A-Z]$') THEN 100 + ASCII(UPPER(rev)) - ASCII('A')
                ELSE 999
              END AS rev_sort
            FROM SMA_MCO_PARAGRAPH
            WHERE {where_clause}
          ),
          ranked AS (
            SELECT
              base.*,
              DENSE_RANK() OVER (
                PARTITION BY drawing_number
                ORDER BY rev_sort DESC
              ) AS rk
            FROM base
          )
          SELECT
            id, value_str, pdf_id, pdf_name, title,
            drawing_number, rev, internal_code,
            project_description, flex_part_number,
            num, create_datetime
          FROM ranked
          WHERE rk = 1
          ORDER BY create_datetime DESC
        """

        # 3. 执行查询
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        # 4. 拼装返回结果
        results = []
        for row in rows:
            (
                para_id, text, pdf_id, pdf_name, title,
                drawing_number, rev, internal_code,
                project_description, flex_part_number,
                num, create_datetime
            ) = row
            results.append({
                "paragraph_id": para_id,
                "text": text,
                "pdf_id": pdf_id,
                "pdf_name": f"{pdf_name}.pdf",
                "title": title,
                "drawing_number": drawing_number,
                "rev": rev,
                "internal_code": internal_code,
                "project_description": project_description,
                "flex_part_number": flex_part_number,
                "num": num,
                "create_datetime": create_datetime,
                "pdf_url": f"/media/pdfs/{pdf_id}.pdf"
            })

        # 5. 返回：只带 results，就不需要前端做分页了
        return SuccessResponse({"results": results})


