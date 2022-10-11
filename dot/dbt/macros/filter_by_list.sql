-- filter the list so that we only keep the words that
-- are in list_of_words 
{% macro filter_by_list(list_to_filter, list_of_words) %}

{% set new_list = [] %}

{% for filter_word in list_to_filter %}
{% set filter_word = filter_word|string %}
{% for word in list_of_words %}
{% if word in filter_word %}
{% do new_list.append(filter_word) %}
{% endif %}
{% endfor %}
{% endfor %}

{{ return(new_list) }}

{% endmacro %}