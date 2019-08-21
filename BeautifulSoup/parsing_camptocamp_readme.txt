----------------------------------------
parsing voies et sorties sur camp to camp
----------------------------------------

entrée utilisateur
	liste des voies (url)	=> obligatoire
	proxy 					=> facultatif
	filtres 				=> to define
		- nb maximum de voies
		- difficulté
		- ...

Traitements / structure des données
	- traitement de la liste en input pour parsing
	- Classe parsing
		- contrôle des url en entrée
		- création d'un dictionnaire
			- clé = url
			- attributs
				- soup html
				- liste des liens des sorties


Restitution
	Classe voie :
		- difficulté maximum
		- orientation
		- approche / descente
		- description des longueurs
		- description des sorties
		- lien

Persistence
	Stockage sqlite
	Classes DAO (modèle à définir)
