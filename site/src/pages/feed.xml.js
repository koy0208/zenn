import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { postSlug } from '../lib/slug';

export async function GET(context) {
  const articles = await getCollection('articles', (e) => e.data.published);
  const posts = await getCollection('posts');

  const items = [
    ...articles.map((e) => ({
      title: e.data.title,
      link: `/articles/${e.id}/`,
      pubDate: e.data.published_at ? new Date(e.data.published_at) : new Date(0),
    })),
    ...posts.map((e) => ({
      title: e.data.title,
      link: `/posts/${postSlug(e.id)}/`,
      pubDate: e.data.date,
    })),
  ].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());

  return rss({
    title: 'データの裏側をあるく',
    description: '技術記事と雑記',
    site: context.site,
    items,
  });
}
