from django.db import IntegrityError
from django import forms
from django.contrib import auth


class LoginForm(forms.Form):
    logName = forms.CharField(label="Имя", max_length=100)
    logPassword = forms.CharField(label="Пароль", max_length=100, widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    regName = forms.CharField(50, label='Имя')
    regPassw1 = forms.CharField(50, label='Пароль', widget=forms.PasswordInput)
    regPassw2 = forms.CharField(50, label='Повтор пароля', widget=forms.PasswordInput)

    def clean(self):
        super(RegistrationForm, self).clean()
        if self.errors:
            print(self.errors)
            return

        regName = self.cleaned_data['regName']
        regPassw1 = self.cleaned_data['regPassw1']
        regPassw2 = self.cleaned_data['regPassw2']
        if regPassw1 == regPassw2:
            print('Пароли совпадают')
            try:
                self.user = auth.models.User.objects.create_user(regName, password=regPassw1)
            except IntegrityError:
                raise forms.ValidationError('Пользователь с таким именем уже существует. Пожалуйста, выберите другое имя')
            except:
                raise forms.ValidationError('Неизвестная ошибка при попытке создать нового пользователя')
        else:
            self.add_error('regPassw1', forms.ValidationError('Пароли не совпадают'))
            self.add_error('regPassw2', forms.ValidationError('Пароли не совпадают'))

