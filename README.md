# Génération de la liste des plans BPE

## Mode d'emploi

Le fichier exécutable à copier se trouve :

:mag_right: GO-OMEXOM BE-Divers BE - Documents\01- LOGICIELS\08 - Scripts\Listing BPE

### :file_folder: Arborecense du projet sous ACC :

<img title="" src="file:///C:/Users/guillaume.barthelemy/AppData/Roaming/marktext/images/2025-07-16-08-11-50-image.png" alt="" width="422">

Il faut créer le dossier "12-BPE" afin d'y placé les plans BPE (Dossier visible par le chantier)

### :file_folder: Arborescence du dossier "12-BPE"

<img title="" src="file:///C:/Users/guillaume.barthelemy/AppData/Roaming/marktext/images/2025-07-16-08-13-06-image.png" alt="" width="434">

Seul les dossiers commençant par "#" ne seront pas pris en compte par le script. Les autres dossier servent à la catégorisation des plans (Libre à chaque technicien de créér ces catégories)

### :file_folder: Arborescence du dossier "#BORDEREAUX"

<img title="" src="file:///C:/Users/guillaume.barthelemy/AppData/Roaming/marktext/images/2025-07-16-08-16-19-image.png" alt="" width="451">

C'est dans ce dossier qu'il faut copier le script exécutable "Listing_BPE". Ce script va répértorier tous les dossiers et fichiers présents dans le dossier "12-BPE" (En dehors des dossiers commençant par "#" et des fichiers présents dans ces derniers).

A l'exécution, ce script crée un fichier récapitualtif des plans BPE (au format PDF avec le nom "Liste BPE - YYYY-MM-DD) ainsi qu'un fichier info.log (Création de ce fichier lors de la première utilisation du script et mise à jours lors des utilisations suivantes).

<img title="" src="file:///C:/Users/guillaume.barthelemy/AppData/Roaming/marktext/images/2025-07-16-08-22-55-image.png" alt="" width="305">

:point_right: Pour que le chantier puisse visualiser les bordereaux d'envoi, ceux ci seront rangés également dans ce dossier.

### Nommage des plans BPE

![](C:\Users\guillaume.barthelemy\AppData\Roaming\marktext\images\2025-07-16-08-27-32-image.png)

Les plans BPE devront obligatoirement être nommés de cette façon :

**NUM_OMEXOM-NUM_CLIENT-INDICE (NUM_ENVOI)**

:warning: Attention à bien respecter les "-", les espaces et les parenthèses
