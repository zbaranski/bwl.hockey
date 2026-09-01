---
layout: default
title: Home
---

# BWL Eishockey — News

{% for post in site.posts %}
<article class="post-preview">
  <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
  <p class="meta">{{ post.date | date: "%d.%m.%Y" }} — {{ post.team }}</p>
  {% if post.image %}
  <img src="{{ post.image }}" alt="" style="max-width: 400px;">
  {% endif %}
  <p>{{ post.excerpt }}</p>
</article>
{% endfor %}
