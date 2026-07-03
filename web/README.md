# web frontend

Phase B の Web/GUI 実装は React + TypeScript + Vite + Tailwind CSS を標準にする。

## セットアップ

```bash
cd web
npm ci
```

## 検証

```bash
npm run lint
npm run format:check
npm run typecheck
```

## 運用ルール

- dev server は `vite --host 127.0.0.1` で localhost に限定する。
- CSS は Tailwind utility / `@theme` design token / `@layer base` を優先する。
- 大量の手書きCSS、CSS Modules の主戦力化、`style` 属性による局所調整は避ける。
- 秘密情報は frontend bundle に入れない。
- React は harness ロジックを直接 import せず、API 境界経由で利用する。
