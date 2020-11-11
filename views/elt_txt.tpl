<h{{rang+2}}> {{'-' * rang}} {{elt['name']}}</h{{rang+2}}>
<ul>
% for link in elt['links']:
<li><a href="{{base_url}}/texte/{{link['idtxt']}}">{{link['titre']}}</a><br /></li>
% end
</ul>
% for child in elt['children']:
% include('elt_txt', base_url=base_url, elt=child, rang=rang+1)
%end
