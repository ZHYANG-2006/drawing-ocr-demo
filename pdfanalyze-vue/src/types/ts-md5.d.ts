declare module 'ts-md5' {
  export function hashStr(value: string): string;
  export function hashBinary(value: Uint8Array): string;
  export function hashObj(value: object): string;
  // Add other exported functions as needed
}
