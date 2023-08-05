from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools
import os

from compas.geometry import Frame
from compas.robots import Inertia
from compas.robots import Inertial
from compas.robots import Joint
from compas.robots import Mass
from compas.robots import Origin

from compas_fab.backends.interfaces import AddAttachedCollisionMesh
from compas_fab.utilities import LazyLoader

pybullet = LazyLoader('pybullet', globals(), 'pybullet')


__all__ = [
    'PyBulletAddAttachedCollisionMesh',
]


class PyBulletAddAttachedCollisionMesh(AddAttachedCollisionMesh):
    """Callable to add a collision mesh and attach it to the robot."""
    def __init__(self, client):
        self.client = client

    def add_attached_collision_mesh(self, attached_collision_mesh, options=None):
        """Add a collision mesh and attach it to the robot.

        Parameters
        ----------
        attached_collision_mesh : :class:`compas_fab.robots.AttachedCollisionMesh`
            Object containing the collision mesh to be attached.
        options : dict
            Dictionary containing the following key-value pairs:

            - ``"robot"``: (:class:`compas_fab.robots.Robot`) Robot instance
              to which the object should be attached.
            - ``"mass"``: (:obj:`float`) The mass of the attached collision
              object.  Defaults to ``1``.
            - ``inertia"``: (:obj:`list`) The elements of the inertia matrix
              of the attached collision object given as
              ``[<ixx>, <ixy>, <ixz>, <iyy>, <iyz>, <izz>]``.  Defaults to
              ``[1., 0., 0., 1., 0., 1.]``.
            - ``"inertial_origin"``: (:class:`compas.geometry.Frame`) This is
              the pose of the inertial reference frame, relative to the link
              reference frame. Defaults to
              :class:`compas.geometry.Frame.worldXY()`.
            - ``"collision_origin"``(:class:`compas.geometry.Frame`) This is
              the pose of the collision reference frame, relative to the link
              reference frame. Defaults to
              :class:`compas.geometry.Frame.worldXY()`.

        Returns
        -------
        ``None``
        """
        robot = options['robot']
        self.client.ensure_cached_robot_geometry(robot)

        mass = options.get('mass', 1.)
        inertia = options.get('inertia', [1., 0., 0., 1., 0., 1.])
        inertial_origin = options.get('inertial_origin', Frame.worldXY())
        collision_origin = options.get('collision_origin', Frame.worldXY())

        cached_robot_model = self.client.get_cached_robot(robot)

        # add link
        mesh = attached_collision_mesh.collision_mesh.mesh
        name = attached_collision_mesh.collision_mesh.id
        mesh_file_name = name + '.stl'
        mesh_fp = os.path.join(self.client._cache_dir.name, mesh_file_name)
        mesh.to_stl(mesh_fp, binary=True)
        link = cached_robot_model.add_link(name, visual_meshes=[mesh], collision_meshes=[mesh])
        mass_urdf = Mass(mass)
        inertia_urdf = Inertia(*inertia)
        inertial_origin_urdf = Origin(inertial_origin.point, inertial_origin.xaxis, inertial_origin.yaxis)
        inertial_urdf = Inertial(inertial_origin_urdf, mass_urdf, inertia_urdf)
        link.inertial = inertial_urdf
        collision_origin_urdf = Origin(collision_origin.point, collision_origin.xaxis, collision_origin.yaxis)
        for element in itertools.chain(link.visual, link.collision):
            element.geometry.shape.filename = mesh_fp
            element.origin = collision_origin_urdf

        # add joint
        parent_link = cached_robot_model.get_link_by_name(attached_collision_mesh.link_name)
        cached_robot_model.add_joint(name + '_fixed_joint', Joint.FIXED, parent_link, link)

        self.client.reload_from_cache(robot)
