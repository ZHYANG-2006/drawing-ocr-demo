// screenfull.d.ts
declare module 'screenfull' {
  const screenfull: {
    isEnabled: boolean;
    toggle: () => Promise<void>;
    on: (event: 'change', callback: () => void) => void;
    isFullscreen: boolean;
  };
  export default screenfull;
}
