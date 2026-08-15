// posts のファイル名は管理用に yyyymmdd_ プレフィックスを付ける。
// URL には日付を含めないため、ここでプレフィックスを取り除く。
export function postSlug(id: string): string {
  return id.replace(/^\d{8}_/, '');
}

// プレフィックス違いの同名（例: 20200812_foo.md と 20241013_foo.md）は
// 同一スラッグに解決して URL が衝突する。黙って 1 本消えるのを防ぐため、
// 重複を検知したらビルドを止める。
export function postSlugs<T extends { id: string }>(entries: T[]): Map<T, string> {
  const seen = new Map<string, string>(); // slug -> 最初に使った id
  const result = new Map<T, string>();
  for (const entry of entries) {
    const slug = postSlug(entry.id);
    const prev = seen.get(slug);
    if (prev && prev !== entry.id) {
      throw new Error(
        `posts のスラッグが衝突しています: "${slug}" (${prev} と ${entry.id})。` +
          `日付プレフィックスを除いたファイル名を一意にしてください。`
      );
    }
    seen.set(slug, entry.id);
    result.set(entry, slug);
  }
  return result;
}
