import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Zenn にも出す技術記事
const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: '../articles' }),
  schema: z.object({
    title: z.string(),
    emoji: z.string().optional(),
    type: z.enum(['tech', 'idea']),
    topics: z.array(z.string()).default([]),
    published: z.boolean().default(false),
    published_at: z.string().optional(),
  }),
});

// 自サイト限定（はてな由来など）
const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: '../posts' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    hatenaPath: z.string().optional(), // 旧 URL を控えておく
  }),
});

export const collections = { articles, posts };
