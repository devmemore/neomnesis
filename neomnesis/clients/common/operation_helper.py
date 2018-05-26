import requests
from neomnesis.common.db.element import Element

class OperationHelper:

    @staticmethod
    def request_modify(server_url, class_id, uuid, field, value):
        url_command = server_url + '/modify_' + class_id
        result = requests.post(url_command, data={'_uuid': uuid, 'field': field, 'value': value})
        return result

    @staticmethod
    def request_insert(server_url, element: Element):
        url_command = server_url + '/insert'
        result = requests.post(url_command, data=element.to_row())
        return result

    @staticmethod
    def request_delete(server_url, class_id, uuid):
        url_command = server_url + '/delete_' + class_id
        result = requests.post(url_command, data={'_uuid': uuid})
        return result

    @staticmethod
    def request_select_statement(server_url, select_statement):
        url_command = server_url + '/select'
        result = requests.post(url_command, data={'select_statement': select_statement})
        return result

    @staticmethod
    def request_commit(server_url, class_id):
        url_command = server_url + '/commit_' + class_id
        result = requests.post(url_command)
        return result

    @staticmethod
    def request_cancel(server_url):
        url_command = server_url + '/cancel'
        result = requests.post(url_command)
        return result

    @staticmethod
    def request_purge(server_url):
        url_command = server_url + '/purge'
        result = requests.post(url_command)
        return result
