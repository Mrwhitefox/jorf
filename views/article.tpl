% if txt.get('ID_ELI'):
lien ELI : <a href="{{txt['ID_ELI']}}">{{txt['ID_ELI']}}</a><br />
% end
<h1>{{txt['TITREFULL']}}</h1>
{{txt['ORIGINE_PUBLI']}}

{{ ! txt['VISAS']}}
% i=0
% for article in txt['STRUCT']['articles']:
<hr />
&gt;<a href=https://www.legifrance.gouv.fr/jorf/article_jo/{{article['ID']}}>Article {{i}}</a>
{{ ! article['BLOC_TEXTUEL']}} <br />
% i = i+1
% end

{{ ! txt['STRUCT']['signataires']}}
