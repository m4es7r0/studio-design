import type * as React from 'react';

export type FormatType = 'money' | 'people' | 'percent' | 'coef' | 'area' | 'count' | 'pp';
export interface Format {
  group(v: number): string;
  money(v: number, opts?: { scale?: 'млн' | 'млрд' | 'трлн' }): string;
  people(v: number): string;
  percent(v: number): string;
  coef(v: number): string;
  area(v: number): string;
  count(v: number, unit?: string): string;
  pp(v: number): string;
  delta(v: number | null | undefined, type: FormatType, unit?: string): string;
  value(v: number | null | undefined, type: FormatType, unit?: string): string;
}
export declare const format: Format;
export type ReactNode = React.ReactNode;

declare global { interface Window { __NAMESPACE__: { format: Format } } }
