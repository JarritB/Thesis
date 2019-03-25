import CifFile

#Het inlezen van een CIF-bestand in een variabele wordt gedaan met de functie:
ciffile = CifFile.ReadCif("bestandsnaam.cif")
#Vervolgens kunnen datablokken worden ingelezen:
datablok = cf["a data block"]
#Of kan een data-element rechtstreeks worden aangesproken met 
dataelement = cf["een datablok"]["een datanaam"]
#De data van loop of lusblok kan worden opgevraagd  
lb = cb.GetLoop("een datanaam uit de loop")  
