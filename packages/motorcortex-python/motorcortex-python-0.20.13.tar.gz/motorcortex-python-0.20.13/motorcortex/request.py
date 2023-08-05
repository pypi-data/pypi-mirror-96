#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2016-2020 VECTIONEER.
#

from motorcortex.reply import Reply

import os
import queue
import ctypes
from concurrent.futures import ThreadPoolExecutor
from pynng import Req0, TLSConfig


class Request(object):

    def __init__(self, protobuf_types, parameter_tree):
        self.__socket = None
        self.__url = None
        self.__connected_lock = None
        self.__protobuf_types = protobuf_types
        self.__parameter_tree = parameter_tree
        self.__pool = ThreadPoolExecutor(max_workers=1)

    def url(self):
        return self.__url

    def connect(self, url, **kwargs):
        conn_timeout_ms, recv_timeout_ms, certificate = self.parse(**kwargs)
        self.__url = url
        tls_config = None
        if certificate:
            tls_config = TLSConfig(TLSConfig.MODE_CLIENT, ca_files=certificate)

        self.__socket = Req0(recv_timeout=recv_timeout_ms, tls_config=tls_config)
        self.__connected_lock = queue.Queue()

        def pre_connect_cb(pipe):
            self.__connected_lock.put(True)

        def post_remove_cb(pipe):
            self.__connected_lock.put(False)

        self.__socket.add_pre_pipe_connect_cb(pre_connect_cb)
        self.__socket.add_post_pipe_remove_cb(post_remove_cb)
        self.__socket.dial(url)

        return Reply(self.__pool.submit(self.waitForConnection, self.__connected_lock,
                                        conn_timeout_ms / 1000.0))

    def close(self):
        if self.__connected_lock:
            self.__connected_lock.put(False)
        self.__socket.close()

    def send(self, encoded_msg, do_not_decode_reply=False):
        if self.__socket is not None:
            return Reply(self.__pool.submit(self.__send, self.__socket, encoded_msg,
                                            None if do_not_decode_reply else self.__protobuf_types))
        return None

    def login(self, login, password):
        """Send a login request to the server

            Args:
                login(str): user login
                password(str): user password

            Results:
                Reply(StatusMsg): A Promise, which resolves if login is successful and fails otherwise.
                Returned message has a status code, which indicates a status of the login.

            Examples:
                >>> login_reply = req.login('operator', 'iddqd')
                >>> login_msg = login_reply.get()
                >>> if login_msg.status == motorcortex_msg.OK
                >>>     print('User logged-in')

        """

        login_msg = self.__protobuf_types.createType('motorcortex.LoginMsg')
        login_msg.password = password
        login_msg.login = login

        return self.send(self.__protobuf_types.encode(login_msg))

    def getParameterTreeHash(self):
        """Request a parameter tree hash from the server.

            Returns:
                Reply(ParameterTreeMsg): A Promise, which resolves when parameter tree hash is received or fails
                otherwise. ParameterTreeHashMsg message has a status field to check the status of the operation.

            Examples:
                >>> param_tree_hash_reply = req.getParameterTreeHash()
                >>> value = param_tree_hash_reply.get()

        """

        # getting and instantiating data type from the loaded dict
        param_tree_hash_msg = self.__protobuf_types.createType('motorcortex.GetParameterTreeHashMsg')

        # encoding and sending data
        return self.send(self.__protobuf_types.encode(param_tree_hash_msg))

    def getParameterTree(self):
        """Request a parameter tree from the server.

            Returns:
                Reply(ParameterTreeMsg): A Promise, which resolves when parameter tree is received or fails
                otherwise. ParameterTreeMsg message has a status field to check the status of the operation.

            Examples:
                >>> param_tree_reply = req.getParameterTree()
                >>> value = param_tree_reply.get()
                >>> parameter_tree.load(value)

        """

        return Reply(self.__pool.submit(self.__getParameterTree,
                                        self.getParameterTreeHash(), self.__protobuf_types, self.__socket))

    def save(self, path, file_name):
        """Request a server to save a parameter tree to file.

            Args:
                path(str): path where to save
                file_name(str): file name

            Returns:
                Reply(StatusMsg): A promise, which resolves when save operation is completed,
                fails otherwise.

        """

        param_save_msg = self.__protobuf_types.createType('motorcortex.SaveMsg')
        param_save_msg.path = path
        param_save_msg.file_name = file_name

        return self.send(self.__protobuf_types.encode(param_save_msg))

    def setParameter(self, path, value, type_name=None):
        """Set new value to a parameter with given path

            Args:
                path(str): parameter path in the tree
                value(any): new parameter value
                type_name(str): type of the value (by default resolved automatically)

            Returns:
                  Reply(StatusMsg): A Promise, which resolves when parameter value is updated or fails otherwise.

            Examples:
                  >>> reply = req.setParameter("root/Control/activateSemiAuto", False)
                  >>> reply.get()
                  >>> reply = req.setParameter("root/Control/targetJointAngles", [0.2, 3.14, 0.4])
                  >>> reply.get()
        """

        return self.send(self.__protobuf_types.encode(self.__buildSetParameterMsg(path, value,
                                                                                  type_name, self.__protobuf_types,
                                                                                  self.__parameter_tree)))

    def setParameterList(self, param_list):
        """Set new values to a parameter list

            Args:
                 param_list([{'path'-`str`,'value'-`any`}]): a list of the parameters which values update

            Returns:
                Reply(StatusMsg): A Promise, which resolves when parameters from the list are updated,
                otherwise fails.

            Examples:
                  >>>  req.setParameterList([
                  >>>   {'path': 'root/Control/generator/enable', 'value': False},
                  >>>   {'path': 'root/Control/generator/amplitude', 'value': 1.4}])

        """

        # instantiating message type
        set_param_list_msg = self.__protobuf_types.createType("motorcortex.SetParameterListMsg")
        # filling with sub messages
        for param in param_list:
            type_name = None
            if "type_name" in param:
                type_name = param["type_name"]
            set_param_list_msg.params.extend([self.__buildSetParameterMsg(param["path"], param["value"],
                                                                          type_name, self.__protobuf_types,
                                                                          self.__parameter_tree)])

        # encoding and sending data
        return self.send(self.__protobuf_types.encode(set_param_list_msg))

    def getParameter(self, path):
        """Request a parameter with description and value from the server.

            Args:
                path(str): parameter path in the tree.

            Returns:
                 Reply(ParameterMsg): Returns a Promise, which resolves when parameter
                 message is successfully obtained, fails otherwise.

            Examples:
                >>> param_reply = req.getParameter('root/Control/actualActuatorPositions')
                >>> param_full = param_reply.get() # Value and description
        """

        return self.send(self.__protobuf_types.encode(self.__buildGetParameterMsg(path, self.__protobuf_types)))

    def getParameterList(self, path_list):
        """Get description and values of requested parameters.

            Args:
                path_list(str): list of parameter paths in the tree.

            Returns:
                Reply(ParameterListMsg): A Promise, which resolves when list of the parameter values is received, fails
                otherwise.

            Examples:
                >>> params_reply = req.getParameter(['root/Control/joint1', 'root/Control/joint2'])
                >>> params_full = params_reply.get() # Values and descriptions
                >>> print(params_full.params)
        """

        # instantiating message type
        get_param_list_msg = self.__protobuf_types.createType('motorcortex.GetParameterListMsg')
        # filling with sub messages
        for path in path_list:
            get_param_list_msg.params.extend([self.__buildGetParameterMsg(path, self.__protobuf_types)])

        # encoding and sending data
        return self.send(self.__protobuf_types.encode(get_param_list_msg))

    def overwriteParameter(self, path, value, force_activate=False, type_name=None):
        """Overwrites actual value of the parameter and depending on the flag forces this value to stay active.
           This method of setting values is useful during debug and installation process, it is not recommended to use
           this method during normal operation.

            Args:
                path(str): parameter path in the tree
                value(any): new parameter value
                force_activate(bool): forces new value to stay active. (by default is set to 'False')
                type_name(str): type of the value (by default resolved automatically)

            Returns:
                  Reply(StatusMsg): A Promise, which resolves when parameter value is updated or fails otherwise.

            Examples:
                  >>> reply = req.overwriteParameter("root/Control/dummyBool", False, True)
                  >>> reply.get()
        """

        return self.send(self.__protobuf_types.encode(self.__buildOverwriteParameterMsg(path, value, force_activate,
                                                                                        type_name,
                                                                                        self.__protobuf_types,
                                                                                        self.__parameter_tree)))

    def releaseParameter(self, path):
        """Deactivate overwrite operation of the parameter.

            Args:
                path(str): parameter path in the tree

            Returns:
                  Reply(StatusMsg): A Promise, which resolves when parameter value is released or fails otherwise.

            Examples:
                  >>> reply = req.releaseParameter("root/Control/dummyBool")
                  >>> reply.get()
        """

        return self.send(self.__protobuf_types.encode(self.__buildReleaseParameterMsg(path, self.__protobuf_types)))

    def createGroup(self, path_list, group_alias, frq_divider=1):
        """Create a subscription group for a list of the parameters.

            This method is used inside Subscription class, use subscription class instead.

            Args:
                path_list(list(str)): list of the parameters to subscribe to
                group_alias(str): name of the group
                frq_divider(int): frequency divider is a downscaling factor for the group publish rate

            Returns:
                Reply(GroupStatusMsg): A Promise, which resolves when subscription is complete,
                fails otherwise.
        """

        # instantiating message type
        create_group_msg = self.__protobuf_types.createType('motorcortex.CreateGroupMsg')
        create_group_msg.alias = group_alias
        create_group_msg.paths.extend(path_list if type(path_list) is list else [path_list])
        create_group_msg.frq_divider = frq_divider if frq_divider > 1 else 1
        # encoding and sending data
        return self.send(self.__protobuf_types.encode(create_group_msg))

    def removeGroup(self, group_alias):
        """Unsubscribe from the group.

            This method is used inside Subscription class, use subscription class instead.

            Args:
                group_alias(str): name of the group to unsubscribe from

            Returns:
                Reply(StatusMsg): A Promise, which resolves when the unsubscribe operation is complete,
                fails otherwise.
        """

        # instantiating message type
        remove_group_msg = self.__protobuf_types.createType('motorcortex.RemoveGroupMsg')
        remove_group_msg.alias = group_alias
        # encoding and sending data
        return self.send(self.__protobuf_types.encode(remove_group_msg))

    @staticmethod
    def __buildSetParameterMsg(path, value, type_name, protobuf_types, parameter_tree):
        param_value = None
        if not type_name:
            type_id = parameter_tree.getDataType(path)
            if type_id:
                param_value = protobuf_types.getTypeByHash(type_id)
        else:
            param_value = protobuf_types.createType(type_name)

        if not param_value:
            print("Failed to find encoder for the path: %s type: %s" % (path, type_name))

        # creating type instance
        set_param_msg = protobuf_types.createType("motorcortex.SetParameterMsg")
        set_param_msg.path = path
        # encoding parameter value
        set_param_msg.value = param_value.encode(value)

        return set_param_msg

    @staticmethod
    def __buildGetParameterMsg(path, protobuf_types):
        # getting and instantiating data type from the loaded dict
        get_param_msg = protobuf_types.createType('motorcortex.GetParameterMsg')
        get_param_msg.path = path

        return get_param_msg

    @staticmethod
    def __buildOverwriteParameterMsg(path, value, activate, type_name, protobuf_types, parameter_tree):
        param_value = None
        if not type_name:
            type_id = parameter_tree.getDataType(path)
            if type_id:
                param_value = protobuf_types.getTypeByHash(type_id)
        else:
            param_value = protobuf_types.createType(type_name)

        if not param_value:
            print("Failed to find encoder for the path: %s type: %s" % (path, type_name))

        # creating type instance
        overwrite_param_msg = protobuf_types.createType("motorcortex.OverwriteParameterMsg")
        overwrite_param_msg.path = path
        overwrite_param_msg.activate = activate
        # encoding parameter value
        overwrite_param_msg.value = param_value.encode(value)

        return overwrite_param_msg

    @staticmethod
    def __buildReleaseParameterMsg(path, protobuf_types):
        release_param_msg = protobuf_types.createType('motorcortex.ReleaseParameterMsg')
        release_param_msg.path = path

        return release_param_msg

    @staticmethod
    def parse(conn_timeout_ms=0, timeout_ms=None, recv_timeout_ms=None, certificate=None, login=None, password=None):
        if timeout_ms and not conn_timeout_ms:
            conn_timeout_ms = timeout_ms

        return conn_timeout_ms, recv_timeout_ms, certificate

    @staticmethod
    def __send(req, encoded_msg, protobuf_types):
        req.send(encoded_msg)
        buffer = req.recv()
        if buffer:
            if protobuf_types:
                return protobuf_types.decode(buffer)
            else:
                return protobuf_types

        return None

    @staticmethod
    def waitForConnection(connected_lock, timeout_sec):
        if timeout_sec <= 0:
            timeout_sec = None
        try:
            return connected_lock.get(block=True, timeout=timeout_sec)
        except queue.Empty:
            return False

    @staticmethod
    def __hash(tree):
        tree_hash = int()

        def clip_u32(val):
            return ctypes.c_uint32(val).value

        for param in tree.params:
            tree_hash += clip_u32(param.data_size + param.data_type + param.id + param.number_of_elements + \
                                  param.param_type + param.unit + param.group_id + param.permissions)
            for ch in param.path:
                tree_hash = clip_u32((tree_hash << 5) - tree_hash) + ord(ch)
                tree_hash |= 0

            if hasattr(param, 'module_type'):
                for ch in param.module_type:
                    tree_hash = clip_u32((tree_hash << 3) - tree_hash) + ord(ch)

        print(tree_hash)

        return tree_hash

    @staticmethod
    def __getParameterTree(hash_reply, protobuf_types, socket):
        tree_hash = hash_reply.get()
        tree = Request.__loadParameterTreeFile(str(tree_hash.hash), protobuf_types)
        if tree:
            if tree_hash.hash == Request.__hash(tree):
                print('Found parameter tree in the cache')
                return tree
            else:
                print('Found parameter tree but the cache does not match')
        else:
            print('Failed to find parameter tree in the cache')

        # getting and instantiating data type from the loaded dict
        param_tree_msg = protobuf_types.createType('motorcortex.GetParameterTreeMsg')
        handle = Request.__send(socket, protobuf_types.encode(param_tree_msg), protobuf_types)

        # encoding and sending data
        return Request.__saveParameterTreeFile(handle, tree_hash.hash)

    @staticmethod
    def __saveParameterTreeFile(parameter_tree, hash):
        print('Saved parameter tree to the cache')
        # cache = Request.__hash(parameter_tree)
        # path = str(cache)
        path = str(hash)
        data = parameter_tree.SerializeToString()
        text_file = open(path, "wb")
        text_file.write(data)
        text_file.close()
        return parameter_tree

    @staticmethod
    def __loadParameterTreeFile(path, protobuf_types):
        if os.path.exists(path):
            text_file = open(path, "rb")
            data = text_file.read()
            text_file.close()
            param_tree_hash_msg = protobuf_types.createType('motorcortex.ParameterTreeMsg')
            param_tree_hash_msg.ParseFromString(data)
            return param_tree_hash_msg
        return None
