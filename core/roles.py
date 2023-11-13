from rolepermissions.roles import AbstractUserRole


class Administrator(AbstractUserRole):
    pass


class Technician(AbstractUserRole):
    pass


class Trainee(AbstractUserRole):
    pass
