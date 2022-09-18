from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone

from .forms import TodoForm
from .models import Todo


def index(request):
    return render(request, 'todo/index.html')


def signup_user(request):
    if request.method == 'GET':
        context = {'form': UserCreationForm()}
        return render(request, 'todo/signup_user.html', context)
    else:
        if request.POST['password1'] == request.POST['password2'] and request.POST['password1'] and request.POST['password2']:
            try:
                # Saving user data and redirecting him to current page
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current')
            except IntegrityError:
                # Handling username that alrerady been taken exception
                context = {'form': UserCreationForm(), 'error': 'This username has already been taken.'}
                return render(request, 'todo/signup_user.html', context)
        elif request.POST['password1'] != request.POST['password2'] and request.POST['password1'] and request.POST['password2']:
            # Handling password not matching exception
            context = {'form': UserCreationForm(), 'error': 'Password did not match. Please try again'}
            return render(request, 'todo/signup_user.html', context)
        else:
            context = {'form': UserCreationForm(), 'error': 'Something went wrong. Maybe You did not enter password?'}
            return render(request, 'todo/signup_user.html', context)


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')


def login_user(request):
    if request.method == 'GET':
        context = {'form': AuthenticationForm()}
        return render(request, 'todo/login_user.html', context)
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if not user:
            context = {'form': AuthenticationForm(),
                       'error': 'Username and password did not match.'}
            return render(request, 'todo/login_user.html', context)
        else:
            login(request, user)
            return redirect('current')


@login_required
def current(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True).order_by('-date_completed')
    context = {'todos': todos}
    return render(request, 'todo/current.html', context)


@login_required
def create_todo(request):
    if request.method == 'GET':
        context = {'form': TodoForm()}
        return render(request, 'todo/create_todo.html', context)
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)

            new_todo.user = request.user
            new_todo.save()
            return redirect('current')
        except ValueError:
            context = {'form': TodoForm(),
                       'error': 'Something went wrong... Try again.'}
            return render(request, 'todo/create_todo.html', context)


@login_required
def todo_view(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        context = {'todo': todo,
                   'form': form}
        return render(request, 'todo/todo_view.html', context)
    else:
        try:
            form = TodoForm(request.POST, instance=todo)  # don't need to create a new object, so we need instance attr
            form.save()
            return redirect('current')

        except ValueError:
            context = {'todo': todo,
                       'error': 'Something went wrong... Try again'}
            return render(request, 'todo/todo_view.html', context)


@login_required
def todo_complete(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('current')


@login_required
def todo_delete(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('current')


@login_required
def completed(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    context = {'todos': todos}
    return render(request, 'todo/completed.html', context)
