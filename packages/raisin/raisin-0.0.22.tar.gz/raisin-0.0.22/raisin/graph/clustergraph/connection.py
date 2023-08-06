#!/usr/bin/env python3

"""
|=========================|
| Les connections reseau. |
|=========================|

* Dans un graphe qui represente un reseau internet, les arcs
relient les machines aux boxes et aux routeurs.
* Modelise un debit variable, le ping ...
"""

import time

from ..segment import Arrow


class Connection(Arrow):
    """
    |====================================|
    | Un cable RJ45 et une carte reseau. |
    |====================================|
    """
    def __init__(self, vs, vd, *, ping=None, flow=None):
        """
        |=============================================|
        | Initialise une representauon de connection. |
        |=============================================|

        Parameters
        ----------
        :param vs: Noeud de depart
        :type vs: Vertex
        :param vd: Noeud d'arrive.
        :type vd: Vertex
        :param ping: Temps du ping en seconde.
        :type ping: float
        :param flow: Debit de communication.
        :type flow: float
        """
        super().__init__(vs, vd)
        self.ping = ping
        self.flow = flow
        self.flags["color"] = "black"

        # Historique.
        self.history = {} # A chaque attribu, associ son etat et sa date de mise a jour.
        if ping:
            self.history["ping"] = time.time()
        if flow:
            self.history["flow"] = time.time()

    def get_attr(self):
        """
        |===================================|
        | Recupere les arguments suffisants |
        | a la reconstitution de self.      |
        |===================================|

        Returns
        -------
        :return: Les clefs et les valeurs a passer a l'initialisateur
            de facon a instancier un nouvel objet de contenu identique a self.
        :rtype: dict
        """
        return {"vs": self.vs.n, "vd": self.vd.n,
            "attr": {"ping": self.ping, "flow": self.flow}}
