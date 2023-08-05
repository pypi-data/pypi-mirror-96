# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import logging

from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Folder, get_options

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Folders:
    """Class dedicated to all "folders" related endpoints"""

    def list_folders(self):
        """List all folders accessible to the authenticated user

        API Endpoint: GET /folders

        :return: a list of folders
        :rtype: list()
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/folders")
        if response.status_code == 200:
            folders_list = list()
            response_list = response.json()
            for folder in response_list:
                sub_folder = Folder.from_json(folder)
                sub_folder.parent = self.rootFolder.id
                folders_list.append(sub_folder)
            return folders_list
        else:
            description = f"Unable to get a list of folders for {self.user.name}"
            raise FossologyApiError(description, response)

    def detail_folder(self, folder_id):
        """Get details of folder.

        API Endpoint: GET /folders/{id}

        :param id: the ID of the folder to be analysed
        :type id: int
        :return: the requested folder
        :rtype: Folder() object
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/folders/{folder_id}")
        if response.status_code == 200:
            detailled_folder = Folder.from_json(response.json())
            for folder in self.folders:
                if folder.id == folder_id:
                    self.folders.remove(folder)
            self.folders.append(detailled_folder)
            return detailled_folder
        else:
            description = f"Error while getting details for folder {folder_id}"
            raise FossologyApiError(description, response)

    def create_folder(self, parent, name, description=None, group=None):
        """Create a new (sub)folder

        The name of the new folder must be unique under the same parent.

        API Endpoint: POST /folders/{id}

        :param parent: the parent folder
        :param name: the name of the folder
        :param description: a meaningful description for the folder (default: None)
        :param group: the name of the group chosen to create the folder (default: None)
        :type parent: Folder() object
        :type name: str
        :type description: str
        :type group: string
        :return: the folder newly created (or already existing) - or None
        :rtype: Folder() object
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user is not allowed to write in the folder or access the group
        """
        headers = {
            "parentFolder": f"{parent.id}",
            "folderName": f"{name}",
            "folderDescription": f"{description}",
        }
        if group:
            headers["groupName"] = group

        response = self.session.post(f"{self.api}/folders", headers=headers)

        if response.status_code == 200:
            logger.info(f"Folder '{name}' already exists")
            for folder in self.folders:
                if folder.name == name:
                    return folder
            logger.error("Folder exists but was not found in the user's folder list")
            return

        elif response.status_code == 201:
            logger.info(f"Folder {name} has been created")
            return self.detail_folder(response.json()["message"])

        elif response.status_code == 403:
            description = f"Folder creation {get_options(group, parent)}not authorized"
            raise AuthorizationError(description, response)
        else:
            description = f"Unable to create folder {name} under {parent}"
            raise FossologyApiError(description, response)

    def update_folder(self, folder, name=None, description=None):
        """Update a folder's name or description

        The name of the new folder must be unique under the same parent.

        API Endpoint: PATCH /folders/{id}

        :param name: the new name of the folder (optional)
        :param description: the new description for the folder (optional)
        :type name: str
        :type description: str
        :return: the updated folder
        :rtype: Folder() object
        :raises FossologyApiError: if the REST call failed
        """
        headers = dict()
        if name:
            headers["name"] = name
        if description:
            headers["description"] = description
        folders_api_path = f"{self.api}/folders/{folder.id}"

        response = self.session.patch(folders_api_path, headers=headers)
        if response.status_code == 200:
            folder = self.detail_folder(folder.id)
            logger.info(f"{folder} has been updated")
            return folder
        else:
            description = f"Unable to update folder {folder.id}"
            raise FossologyApiError(description, response)

    def delete_folder(self, folder):
        """Delete a folder

        API Endpoint: DELETE /folders/{id}

        :param folder: the Folder to be deleted
        :type folder: Folder() object
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.delete(f"{self.api}/folders/{folder.id}")
        if response.status_code == 202:
            logger.info(f"Folder {folder.id} has been scheduled for deletion")
        else:
            description = f"Unable to delete folder {folder.id}"
            raise FossologyApiError(description, response)

    def _put_folder(self, action, folder, parent):
        """Copy or move a folder

        Internal function meant to be called by move_folder() or copy_folder()

        API Endpoint: PUT /folders/{id}

        :param action: "move" or "copy"
        :param action: string
        :param folder: the Folder to be moved or copied
        :type folder: Folder() object
        :param parent: the new parent folder
        :type parent: Folder() object
        :return: the updated folder
        :rtype: Folder() object
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"parent": str(parent.id), "action": action}
        response = self.session.put(f"{self.api}/folders/{folder.id}", headers=headers)
        if response.status_code == 202:
            logger.info(f"Folder {folder.name} has been {action}d to {parent.name}")
            return self.detail_folder(folder.id)
        else:
            description = f"Unable to {action} folder {folder.name} to {parent.name}"
            raise FossologyApiError(description, response)

    def copy_folder(self, folder, parent):
        """Copy a folder

        :param folder: the Folder to be copied
        :type folder: Folder() object
        :param parent: the new parent folder
        :type parent: Folder() object
        :return: the updated folder
        :rtype: Folder() object
        :raises FossologyApiError: if the REST call failed
        """
        return self._put_folder("copy", folder, parent)

    def move_folder(self, folder, parent):
        """Move a folder

        :param folder: the Folder to be moved
        :type folder: Folder() object
        :param parent: the new parent folder
        :type parent: Folder() object
        :return: the updated folder - or None if the REST call failed
        :rtype: Folder() object
        :raises FossologyApiError: if the REST call failed
        """
        return self._put_folder("move", folder, parent)
