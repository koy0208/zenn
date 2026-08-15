# Zenn CLI

* [📘 How to use](https://zenn.dev/zenn/articles/zenn-cli-guide)

## サイト (koylog.com) のデプロイ

`site/` の Astro サイトを Cloudflare Workers (static assets) で配信している。

デプロイ設定はリポジトリルートの `wrangler.jsonc` に集約してあり、`build` フックが
`site/` で `npm ci && npm run build` を実行してから `site/dist` をアップロードする。

```sh
# リポジトリルートで実行すること（site/ からではない）
npx wrangler deploy

# アップロード内容の確認だけしたい場合
npx wrangler deploy --dry-run
```

Cloudflare Workers Builds は push をトリガーにリポジトリルートで `npx wrangler deploy`
を実行するため、ダッシュボード側にビルドコマンドを設定する必要はない。