-- filter out word_to_filter from list.
{% macro filter_by_word(list_to_filter, word_to_filter) %}

{% set new_list = [] %}

{% for word in list_to_filter %}
{% set word = word|string %}
{% if word_to_filter in word %}
{{ log("(filter_by_word macro output) Filtered word from list: " ~ word, info=True) }}
{% else %}
{% do new_list.append(word) %}
{% endif %}
{% endfor %}

{{ return(new_list) }}

{% endmacro %}