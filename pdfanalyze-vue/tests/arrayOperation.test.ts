import {
  judementSameArr,
  isObjectValueEqual,
  removeDuplicate,
} from '../src/utils/arrayOperation';

describe('Array Operations', () => {
  // 测试 judementSameArr 函数
  test('judementSameArr should return true for identical arrays', () => {
    const newArr = ['a', 'b', 'c'];
    const oldArr = ['a', 'b', 'c'];
    expect(judementSameArr(newArr, oldArr)).toBe(true);
  });

  test('judementSameArr should return false for different arrays', () => {
    const newArr = ['a', 'b', 'd'];
    const oldArr = ['a', 'b', 'c'];
    expect(judementSameArr(newArr, oldArr)).toBe(false);
  });

  // 测试 isObjectValueEqual 函数
  test('isObjectValueEqual should return true for identical objects', () => {
    const obj1 = { name: 'Alice', age: 25 };
    const obj2 = { name: 'Alice', age: 25 };
    expect(isObjectValueEqual(obj1, obj2)).toBe(true);
  });

  test('isObjectValueEqual should return false for different objects', () => {
    const obj1 = { name: 'Alice', age: 25 };
    const obj2 = { name: 'Bob', age: 30 };
    expect(isObjectValueEqual(obj1, obj2)).toBe(false);
  });

  // 测试 removeDuplicate 函数
  test('removeDuplicate should remove duplicates in a simple array', () => {
    const arr = ['a', 'b', 'a', 'c'];
    expect(removeDuplicate(arr)).toEqual(['a', 'b', 'c']);
  });

  test('removeDuplicate should remove duplicates in array of objects by attr', () => {
    const arr = [
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
      { id: 1, name: 'Alice' },
    ];
    expect(removeDuplicate(arr, 'id')).toEqual([
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
    ]);
  });
});
