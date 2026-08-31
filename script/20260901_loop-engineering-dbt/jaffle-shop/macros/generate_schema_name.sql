{#
  カスタムスキーマ名をそのまま使う（デフォルトの "target_custom" 連結をやめる）。
  seeds を raw スキーマに、モデルを main スキーマに置くための設定。
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
