export type EntryDate = {
  date: Date;
  /** ファイル名が YYYYMM までしか持たない場合は日が不明 */
  hasDay: boolean;
};

/** ファイル名先頭の YYYYMMDD / YYYYMM から日付を推定する */
export function dateFromId(id: string): EntryDate | null {
  const m = id.match(/(\d{4})(\d{2})(\d{2})?/);
  if (!m) return null;
  const [, y, mo, d] = m;
  return {
    date: new Date(Number(y), Number(mo) - 1, d ? Number(d) : 1),
    hasDay: Boolean(d),
  };
}

/** 一覧用の等幅表記。日が不明なら月だけ返す（例: 12.02 / 12） */
export function shortDate({ date, hasDay }: EntryDate): string {
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  if (!hasDay) return mm;
  return `${mm}.${String(date.getDate()).padStart(2, '0')}`;
}

/** 記事ページ用の和文表記（例: 2025年12月2日） */
export function longDate({ date, hasDay }: EntryDate): string {
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: 'long',
    ...(hasDay ? { day: 'numeric' } : {}),
  });
}

/** <time datetime> 用 */
export function isoDate({ date, hasDay }: EntryDate): string {
  const ymd = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  return hasDay ? `${ymd}-${String(date.getDate()).padStart(2, '0')}` : ymd;
}
