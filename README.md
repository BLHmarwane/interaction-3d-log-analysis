# Interaction 3D Log Analysis

Ce depot presente une tache realisee dans le cadre de mon stage autour de la validation de modalites d'interaction et de fonctionnalites a integrer dans un logiciel en phase d'essai clinique. Cette tache s'inscrivait dans un contexte plus large : evaluer comment un utilisateur peut manipuler un modele 3D de maniere precise, stable et intuitive dans un environnement medico-chirurgical.

L'objectif de cette partie etait de mettre en place une chaine d'analyse permettant de comparer plusieurs modalites a partir de logs de manipulation et de retours utilisateurs. Le depot se concentre donc sur la partie analyse des donnees et interpretation des resultats.

Le simulateur utilise pour tester les modalites et produire les logs de transformation est presente dans le depot associe :

[Manual Registration Simulator V2](https://github.com/BLHmarwane/ManualRegistrationGL_V2)

## Modalites et perimetre

Les modalites etudiees sont :

- `SpaceMouse`
- `Mouse2D`
- `Trackpad`
- `HandGrab`

L'analyse quantitative porte uniquement sur `SpaceMouse`, `Mouse2D` et `Trackpad`, car ces trois modalites disposent de matrices de transformation comparables. `HandGrab` est garde dans l'analyse qualitative seulement, car il a ete evalue a travers les retours utilisateurs mais ne disposait pas de logs matriciels equivalents.

## Methode

Pour cette partie du stage, j'ai d'abord concu un simulateur independant afin de tester differentes modalites d'interaction avant leur integration eventuelle dans le logiciel principal. Cette separation permettait d'experimenter plus librement sur les interactions, sans impacter directement le logiciel utilise dans le contexte d'essai clinique.

Dans ce simulateur, j'ai ajoute un systeme de logs base sur les matrices de transformation. A la fin de chaque essai, le simulateur enregistre la transformation cible et la transformation finale obtenue par l'utilisateur. Ces logs sont ensuite traites separement dans ce depot afin de realiser l'analyse quantitative.

En parallele, les retours utilisateurs sont gardes pour l'analyse qualitative. Cette separation permet de comparer les performances mesurees dans les logs avec le ressenti utilisateur, sans melanger les deux types de donnees.

Chaque essai quantitatif est represente par deux matrices 4x4 :

- une matrice cible, qui represente la position et l'orientation attendues ;
- une matrice finale, qui represente la position et l'orientation obtenues apres manipulation.

L'erreur est calculee en comparant ces deux matrices :

```text
T_error = inverse(T_target) @ T_final
```

Les metriques principales sont ensuite extraites :

- erreur de translation en millimetres ;
- erreur de rotation en degres ;
- temps de realisation ;
- longueur du chemin ;
- scores qualitatifs issus du questionnaire.

Les donnees generees localement ne sont pas publiees dans ce depot. Seuls le code, les figures et ce README sont versionnes.

## Analyse quantitative

La premiere comparaison concerne l'erreur de translation. La `SpaceMouse` obtient les erreurs les plus faibles et la dispersion la plus reduite. `Mouse2D` presente les erreurs les plus importantes, tandis que `Trackpad` se situe entre les deux.

![Erreur de translation par modalite](figures/01_boxplot_translation_error.png)

L'erreur de rotation suit la meme tendance. La `SpaceMouse` reste la modalite la plus precise, ce qui est important pour des manipulations 3D fines. `Mouse2D` et `Trackpad` montrent davantage de variabilite.

![Erreur de rotation par modalite](figures/02_boxplot_rotation_error.png)

Le temps de realisation est aussi plus favorable avec la `SpaceMouse`. Cela indique que la modalite permet non seulement d'etre plus precise, mais aussi d'atteindre la position cible plus rapidement.

![Temps de realisation par modalite](figures/03_boxplot_completion_time.png)

La longueur du chemin confirme cette lecture : une trajectoire plus courte traduit une manipulation plus directe, avec moins d'ajustements inutiles.

![Longueur de chemin par modalite](figures/04_boxplot_path_length.png)

## Analyse qualitative

L'analyse qualitative ajoute `HandGrab`, car cette modalite est interessante du point de vue utilisateur. Elle est percue comme intuitive, mais elle reste separee de l'analyse quantitative faute de logs comparables.

![Scores qualitatifs par modalite](figures/06_qualitative_scores_by_modality.png)

Les votes de preference montrent que la `SpaceMouse` reste la modalite la plus appreciee globalement. `HandGrab` arrive ensuite, surtout grace a son aspect naturel et intuitif.

![Votes de preference finale](figures/07_preference_votes.png)

## Synthese

Le radar suivant resume les performances quantitatives relatives. Il permet de visualiser rapidement le compromis entre precision, rapidite et stabilite.

![Performance quantitative relative](figures/08_summary_radar_optional.png)

Globalement, la `SpaceMouse` ressort comme la modalite la plus equilibree. Elle donne de meilleurs resultats en precision, en temps de realisation et en stabilite de trajectoire. Le `Trackpad` reste utilisable, mais moins stable. `Mouse2D` est plus familiere, mais moins adaptee aux manipulations 3D precises. `HandGrab` est interessant qualitativement, surtout pour son intuitivite, mais il demande une evaluation quantitative plus comparable pour etre juge au meme niveau.

Cette tache m'a permis de mettre en place une demarche complete d'analyse : partir de logs de transformation, extraire des metriques utiles, comparer plusieurs modalites et presenter les resultats de maniere lisible.
