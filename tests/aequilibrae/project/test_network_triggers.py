from unittest import TestCase
import sqlite3
from tempfile import gettempdir
import os
import uuid
from shutil import copytree
from shapely.geometry import Point
from aequilibrae.project import Project
from aequilibrae.project.project_creation import remove_triggers, add_triggers
from ...data import siouxfalls_project


class TestNetworkTriggers(TestCase):
    def setUp(self) -> None:
        os.environ['PATH'] = os.path.join(gettempdir(), 'temp_data') + ';' + os.environ['PATH']
        self.proj_path = os.path.join(gettempdir(), f'aeq_{uuid.uuid4().hex}')
        copytree(siouxfalls_project, self.proj_path)
        self.siouxfalls = Project()
        self.siouxfalls.open(self.proj_path)
        remove_triggers(self.siouxfalls.conn)
        add_triggers(self.siouxfalls.conn)

    def tearDown(self) -> None:
        self.siouxfalls.close()

    def test_delete_links_delete_nodes(self):
        items = self.siouxfalls.network.count_nodes()
        self.assertEqual(24, items, 'Wrong number of nodes found')
        links = self.siouxfalls.network.links
        nodes = self.siouxfalls.network.nodes

        node = nodes.get(1)
        node.is_centroid = 0
        node.save()

        # We have completely disconnected 2 nodes (1 and 2)
        for i in [1, 2, 3, 4, 5, 14]:
            link = links.get(i)
            link.delete()
        # Since node 1 is no longer a centroid, we should have only 23 nodes in the network
        items = self.siouxfalls.network.count_nodes()
        self.assertEqual(23, items, 'Wrong number of nodes found')

    def test_add_empty_node(self):
        self.assertEqual(24, self.siouxfalls.network.count_nodes(), 'Wrong number of nodes found')

        sql = 'INSERT into nodes (node_id, is_centroid, modes, link_types, geometry) VALUES(?,?,?,?,GeomFromWKB(?, 4326));'

        data = [1000, 0, 'c', 'y', Point(0, 0).wkb]
        curr = self.siouxfalls.conn.cursor()

        with self.assertRaises(sqlite3.IntegrityError):
            curr.execute(sql, data)

        data[1] = 1
        curr.execute(sql, data)
        self.siouxfalls.conn.commit()
        self.assertEqual(25, self.siouxfalls.network.count_nodes(), 'Failed to add node')