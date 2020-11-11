Référence texte : {{jo['ID']}}<br >
Lien ELI : <a href={{jo['ID_ELI']}}>{{jo['ID_ELI']}} </a><br />
<br />
<h1>{{jo['TITRE']}}</h1>
<br />
% include('elt_txt', base_url=base_url, elt=jo['STRUCTURE_TXT']['children'][0], rang=0)
