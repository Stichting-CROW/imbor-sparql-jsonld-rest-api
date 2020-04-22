class OtlQueries:
    def __init__(self):
        self.prefix_groep = "<http://linkeddata.crow.nl/publication-v2/ns/crow/imbor/version/1243521994744365056/def/groepering/>"
        self.prefix_nta8035 = "<https://w3id.org/def/basicsemantics-owl#>"

    def selecteer_vakdisciplines(self):
        return (
            """ 
     PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX groep: """
            + self.prefix_groep
            + """
    
        SELECT ?VakdisciplineURI ?VakdisciplineLabel
          WHERE {
            groep:IMBORVakdisciplineCollectie skos:member ?VakdisciplineURI .
            ?VakdisciplineURI skos:prefLabel ?VakdisciplineLabel .
          }
    """
        )

    def selecteer_objecttypen_per_vakdiscipline(self, vakdiscipline):
        return (
            """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?VakdisciplineURI ?VakdisciplineLabel ?FysiekObjectURI ?FysiekObjectLabel
        WHERE {
        # Selecteer de klasse Wegen binnen de groeperingen ...
            BIND (\""""
            + vakdiscipline
            + """\"@nl-NL as ?VakdisciplineLabel)
            ?VakdisciplineURI a skos:Collection;
            skos:prefLabel ?VakdisciplineLabel;
         # ... en laat de members van die groep zien.                          
            skos:member ?FysiekObjectURI .
            ?FysiekObjectURI skos:prefLabel ?FysiekObjectLabel .
        }
        ORDER BY ?FysiekObjectLabel
    """
        )

    def selecteer_collecties(self):
        return (
            """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX groep:  """
            + self.prefix_groep
            + """
    
              SELECT (?memberLabel as ?collecties)
              WHERE {
                  groep:IMBORHierarchischeCollectie skos:member ?member .
                  ?member skos:prefLabel ?memberLabel .
              } order by ?member
    """
        )

    def selecteer_objecttypegroepen(self):
        return (
            """
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX groep:  """
            + self.prefix_groep
            + """
            
            SELECT ?objecttypegroepURI ?objecttypegroepLabel
            WHERE {
                groep:Objecttypegroep skos:member ?objecttypegroepURI .
                ?objecttypegroepURI skos:prefLabel ?objecttypegroepLabel .
            }
        """
        )

    def selecteer_beheerobjecten(self):
        return (
            """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX nta8035: """
            + self.prefix_nta8035
            + """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                
                SELECT (?thing AS ?FysiekObjectURI) ?FysiekObjectLabel ?FysiekObjectDefinitie 
                WHERE {
                # Selecteer alleen klassen ...
                    ?thing a rdfs:Class ; 
                # ... die een directe subklasse zijn van NTA8035 Fysiek object ...
                           rdfs:subClassOf nta8035:PhysicalObject ; 
                # ... en een preferred label hebben ...
                           skos:prefLabel ?FysiekObjectLabel ; 
                # ... en een definitie hebben.
                           skos:definition ?FysiekObjectDefinitie .
                }
                ORDER BY ?FysiekObjectLabel
           """
        )

    def selecteer_eigenschappen_per_beheerobject(self, beheerobject):
        return (
            """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX nta8035: """
            + self.prefix_nta8035
            + """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                
                SELECT ?FysiekObjectURI ?FysiekObjectLabel ?EigenschapURI ?EigenschapLabel ?EigenschapVanObjectLabel
                
                WHERE {
                
                # Het kan zien dat dit aangepast moet worden naar subClassOf nta8035:PhysicalObject
                            ?FysiekObjectURI skos:prefLabel ?preflabel .
                            
                # ... alleen binnen IMBOR objecten.
                            FILTER regex(str(?FysiekObjectURI), "crow/imbor")
                            
                            FILTER (LCASE(str(?preflabel)) = \""""
            + beheerobject.lower()
            + """\") # heel woord
                            BIND (?preflabel AS ?FysiekObjectLabel)
                            
                # Trek het property-path uit elkaar, maak de SHACL shapes optioneel, deze zijn niet altijd aanwezig
                            ?FysiekObjectURI rdfs:subClassOf* ?SuperKlasse .
                            ?SuperKlasse skos:prefLabel ?EigenschapVanObjectLabel .
                            
                    OPTIONAL
                    {
                            ?SHACLNodeShape sh:targetClass ?SuperKlasse .
                            ?SHACLNodeShape sh:property ?SHACLPropertyShape .
                
                # Laat de relatie zien van de SHACL Shape, naar de eigenschap.
                            ?SHACLPropertyShape sh:path ?EigenschapURI .
                            ?EigenschapURI skos:prefLabel ?EigenschapLabel .
                
                # En filter de hasPart relaties eruit om alleen echte eigenschappen te zien.
                            MINUS { ?SHACLPropertyShape sh:path nta8035:hasPart }
                    }
                }
                
                ORDER BY str(?FysiekObjectLabel) str(?EigenschapLabel) str(?EigenschapVanObjectLabel)
           """        )

