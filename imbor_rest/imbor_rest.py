from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_talisman import Talisman
from .crow_ldp_caller import CrowLdp
from .queries import OtlQueries
from flask_cors import CORS
from pyld import jsonld
import json

app = Flask(__name__)
# let op, hier verwijzen naar de juiste config file met api keys
app.config.from_pyfile(r"./config/ldp_config.cfg")
if app.config["CORS"]:
    cors = CORS(app)
# TODO: https implementeren...
# Talisman(app)

crow_ldp = CrowLdp(
    clientId=app.config["CLIENTID"],
    toolId=app.config["TOOLID"],
    privateKey=app.config["PRIVATEKEY"],
    base_url=app.config["BASE_URL"],
)

otl_queries = OtlQueries()


class CONTEXTS:
    Beheerobject = {
        "@language": "nl-nl",
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "prefLabel": "http://www.w3.org/2004/02/skos/core#prefLabel",
        "subClassOf": {
            "@id": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            "@type": "@id",
        },
        "guid": {
            "@id": "http://www.w3.org/2004/02/skos/core#notation",
            "@type": "@id",
        },
        "definition": "http://www.w3.org/2004/02/skos/core#definition",
    }


def swagger_property_schema_for_jsonld_context(context):
    schema = dict()

    for k, v in context.items():
        if isinstance(v, dict):
            if v["@type"] == "@id":
                schema[k] = {"type": "string", "format": "uri"}
                continue

        if "@" in k:
            continue

        schema[k] = {"type": "string"}

    return schema


swagger = Swagger(
    app,
    template={
        "swagger": "3.0",
        "openapi": "3.0.0",
        "info": {"title": "imbor", "version": "0.1.0",},
        "components": {
            "schemas": {
                "Collecties": {"properties": {"naam": {"type": "string"}}},
                "Vakdisciplines": {
                    "properties": {
                        "VakdisciplineURI": {"type": "string", "format": "uri"},
                        "VakdisciplineLabel": {"type": "string"},
                    }
                },
                "Objecttypegroepen": {
                    "properties": {
                        "objecttypegroepURI": {"type": "string", "format": "uri"},
                        "objecttypegroepLabel": {"type": "string"},
                    }
                },
                "Objecttypen": {
                    "properties": {
                        "VakdisciplineURI": {"type": "string", "format": "uri"},
                        "VakdisciplineLabel": {"type": "string"},
                        "FysiekObjectURI": {"type": "string", "format": "uri"},
                        "FysiekObjectLabel": {"type": "string"},
                    }
                },
                "beheerobjecten": {
                    "properties": swagger_property_schema_for_jsonld_context(
                        CONTEXTS.Beheerobject
                    )
                },
                "beheerobject_eigenschappen": {
                    "properties": {
                        "FysiekObjectURI": {"type": "string", "format": "uri"},
                        "FysiekObjectLabel": {"type": "string"},
                        "EigenschapURI": {"type": "string", "format": "uri"},
                        "EigenschapLabel": {"type": "string"},
                        "EigenschapVanObjectLabel": {"type": "string"},
                    }
                },
            }
        },
    },
)


@app.route("/collecties/")
def get_collecties():
    """
    Get all collecties
    ---
    description: Get all collecties.
    tags:
      - collecties
    responses:
      200:
        description: List of all collecties.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Collecties'

    """

    res = crow_ldp.run_query(otl_queries.selecteer_collecties())

    return res, 200


@app.route("/vakdisciplines/")
def get_vakdisciplines():
    """
    Get all vakdisciplines
    ---
    description: Get all vakdisciplines.
    tags:
      - vakdisciplines
    responses:
      200:
        description: List of all vakdisciplines.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Vakdisciplines'

    """

    res = crow_ldp.run_query(otl_queries.selecteer_vakdisciplines())

    return res, 200


@app.route("/objecttypegroepen/")
def get_objecttypegroepen():
    """
    Get all objecttypegroepen
    ---
    description: Get all objecttypegroepen.
    tags:
      - objecttypegroepen
    responses:
      200:
        description: List of all objecttypegroepen.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Objecttypegroepen'

    """

    res = crow_ldp.run_query(otl_queries.selecteer_objecttypegroepen())

    return res, 200


@app.route("/vakdisciplines/<string:discipline>/")
def get_objecttypen_per_vakdiscipline(discipline):
    """
    Get all objecttypen per vakdiscipline
    ---
    description: Get all objecttypen per vakdiscipline.
    tags:
      - vakdisciplines
    parameters:
        - name: discipline
          in: path
          required: true
          description: De discipline naam
          schema:
              type: string
    responses:
      200:
        description: List of all objecttypen per vakdisciplines.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Objecttypen'

    """

    res = crow_ldp.run_query(
        otl_queries.selecteer_objecttypen_per_vakdiscipline(discipline)
    )

    return res, 200


@app.route("/beheerobjecten/")
def get_beheerobjecten():
    """
    Get all beheerobjecten
    ---
    description: Get all beheerobjecten.
    tags:
      - beheerobjecten
    responses:
      200:
        description: alle beheerobjecten.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/beheerobjecten'

    """

    res = crow_ldp.run_query(otl_queries.selecteer_beheerobjecten())

    # limit en paging

    response = list()

    for beheerobject in res:
        response.append(jsonld.compact(beheerobject, CONTEXTS.Beheerobject))

    # print(type(res))

    return (
        json.dumps(response, ensure_ascii=False),
        200,
        {"Content-Type": "application/ld+json"},
    )


@app.route("/beheerobjecten/<string:beheerobject>/")
def get_eigenschappen_per_beheerobject(beheerobject):
    """
    Get all eigenschappen per beheerobject
    ---
    description: Get all eigenschappen per beheerobject.
    tags:
      - beheerobjecten
    parameters:
        - name: beheerobject
          in: path
          required: true
          description: beheerobject naam
          schema:
              type: string
    responses:
      200:
        description: alle eigenschappen van het beheerobject.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/beheerobject_eigenschappen'

    """

    res = crow_ldp.run_query(
        otl_queries.selecteer_eigenschappen_per_beheerobject(beheerobject)
    )

    return res, 200
