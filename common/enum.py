def get_uploaded_file_status(status):
    status_dict = {'processing': 1, 'done': 2, 'error': 3}
    if type(status).__name__ == 'int':
        for key, value in status_dict.items():
            if value == status:
                return key

    if status_dict.get(status):
        return status_dict[status]
    return 0


def get_mp4_file_status(status):
    status_dict = {'processing': 1, 'done': 2, 'error': 3}
    if type(status).__name__ == 'int':
        for key, value in status_dict.items():
            if value == status:
                return key

    if status_dict.get(status):
        return status_dict[status]
    return 0


def get_user_status(status):
    status_dict = {'pending': 1, 'active': 2, 'deactivate': 3, 'deleted': 4}
    if type(status).__name__ == 'int':
        for key, value in status_dict.items():
            if value == status:
                return key

    if status_dict.get(status):
        return status_dict[status]
    return 0

