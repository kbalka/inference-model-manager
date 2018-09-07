import falcon
from management_api.utils.logger import get_logger

logger = get_logger(__name__)


class ManagementApiException(Exception):

    @staticmethod
    def handler(ex, req, resp, params):
        logger.error(str(ex))
        raise falcon.HTTPBadRequest(str(ex))


class KubernetesCallException(ManagementApiException):
    def __init__(self, object_name, k8s_api_exception):
        self.object_name = object_name
        self.k8s_api_exception = k8s_api_exception
        super().__init__(k8s_api_exception)

    def form_response(self, message):
        if 400 <= self.k8s_api_exception.status < 500:
            raise falcon.HTTPBadRequest(message)
        else:
            raise falcon.HTTPInternalServerError(message)


class KubernetesCreateException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during {} creation: {}"
        logger.error(message.format(ex.object_name, str(ex)))
        ex.form_response(message.format(ex.object_name, ex.reason))


class KubernetesDeleteException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during {} deletion: {}"
        logger.error(message.format(ex.object_name, str(ex)))
        ex.form_response(message.format(ex.object_name, ex.reason))


class KubernetesGetException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during reading {} object: {}"
        logger.error(message.format(ex.object_name, str(ex)))
        ex.form_response(message.format(ex.object_name, ex.reason))


class KubernetesUpdateException(KubernetesCallException):
    @staticmethod
    def handler(ex, req, resp, params):
        message = "An error occurred during {} update: {}"
        logger.error(message.format(ex.object_name, str(ex)))
        ex.form_response(message.format(ex.object_name, ex.reason))


class MinioCallException(ManagementApiException):
    def __init__(self, message):
        super().__init__("MINIO FAILURE: " + message)

    @staticmethod
    def handler(ex, req, resp, params):
        logger.error(str(ex))
        raise falcon.HTTPInternalServerError(str(ex))


class TenantAlreadyExistsException(ManagementApiException):
    def __init__(self, tenant_name):
        super().__init__()
        self.tenant_name = tenant_name

    @staticmethod
    def handler(ex, req, resp, params):
        message = "Tenant {} already exists".format(ex.tenant_name)
        logger.error(message)
        raise falcon.HTTPConflict(message)


class TenantDoesNotExistException(ManagementApiException):
    def __init__(self, tenant_name):
        super().__init__()
        self.tenant_name = tenant_name

    @staticmethod
    def handler(ex, req, resp, params):
        message = "Tenant {} does not exist".format(ex.tenant_name)
        logger.error(message)
        raise falcon.HTTPNotFound(title=message)


class InvalidParamException(ManagementApiException):
    def __init__(self, param, error_message, validity_rules_message=None):
        super().__init__(error_message)
        self.validity_rules_message = validity_rules_message
        self.param = param

    @staticmethod
    def handler(ex, req, resp, params):
        response_message = str(ex) + " " + ex.validity_rules_message
        logger.error(str(ex))
        raise falcon.HTTPInvalidParam(response_message, ex.param)


class MissingParamException(ManagementApiException):
    def __init__(self, param):
        super().__init__(param + " parameter required")
        self.param = param

    @staticmethod
    def handler(ex, req, resp, params):
        logger.error(str(ex))
        raise falcon.HTTPMissingParam(ex.param)


custom_errors = [ManagementApiException, KubernetesCallException, KubernetesDeleteException,
                 KubernetesCreateException, KubernetesGetException, KubernetesUpdateException,
                 MinioCallException, TenantAlreadyExistsException, TenantDoesNotExistException,
                 InvalidParamException]


def default_exception_handler(ex, req, resp, params):
    message = "Unexpected error occurred: {} ".format(ex)
    logger.error(message + "Request: {}  Params: {}".format(req, params))
    raise falcon.HTTPInternalServerError(message)


def add_error_handlers(falcon_api):
    falcon_api.add_error_handler(Exception, default_exception_handler)
    for error in custom_errors:
        falcon_api.add_error_handler(error, error.handler)

