    def create_user(self, first_name, last_name, email, telNumber, password=None):
        user = self.model(
            email=self.normalize_email(email),
            telNumber=telNumber,
            first_name=first_name,
            last_name=last_name
        )
        user.username = email.split('@')[0]
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, telNumber, password):
        user = self.create_user(
            email,
            password=password,
            telNumber=telNumber,
        )
        user.username = email.split('@')[0]
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, telNumber, password):
        user = self.create_user(
            email,
            password=password,
            telNumber=telNumber,
            first_name=first_name,
            last_name=last_name
        )
        user.username = email.split('@')[0]
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user