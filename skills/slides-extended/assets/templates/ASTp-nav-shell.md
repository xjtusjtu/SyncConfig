<!-- Generic nav shell: header / content / footer slots.
     Per-slide usage:
       template="[[ASTp-nav-shell]]"
       ::: header  p = deck title (#0), ul = nav; ==mark== current chapter
       ::: footer  …
       (body → content)
-->

<grid drag="100 8" class="header steps bg-with-dark-color" drop="topleft" flow="row" pad="0 40px" align="justify">
<% header %>
</grid>

<grid class="as-body" drag="100 85" drop="0 10" align="topleft" pad="40px">
<% content %>
</grid>

<grid drag="100 4" drop="bottom" class="footer steps">
<% footer %>
</grid>
