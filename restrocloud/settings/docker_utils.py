import os


def get_secret_from_docker(environment_variable):
    '''
    returns content of environment_variable or environment_variable_FILE 's content
    POSTGRES_PASSWORD or cat POSTGRES_PASSWORD_FILE => 'postgrespassword'
    :param environment_variable:
    :return:
    '''
    secret_key_env = os.environ.get(environment_variable)
    secret_key_file = os.environ.get(environment_variable + '_FILE')

    if secret_key_env:
        return secret_key_env
    if secret_key_file:
        try:
            return open(secret_key_file, 'r').read().strip()
        except:
            return None
