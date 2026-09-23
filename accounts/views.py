from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm,ProfileForm
from orders.models import Order
# Create your views here.

def register(request):
    if request.method =="POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user =form.save()
            login(request, user)

            if user.role == 'shop_owner':
                return redirect('shop_dashboard')

            return redirect('customer_dashboard')

    else:
        form =RegisterForm()

    template_name ="accounts/register.html"
    context ={'form':form}
    return render(request, template_name, context)


def user_login(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user =authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)

            if user.role == 'shop_owner':
                return redirect('shop_dashboard')
            return redirect('customer_dashboard')

        return render(request,'accounts/login.html',{'error':'Invalid username or password'})

    return render(request,'accounts/login.html')

def user_logout(request):

    logout(request)

    return (redirect('login'))


@login_required
def profile(request):

    orders = Order.objects.filter(
        customer=request.user
    )

    total_orders = orders.count()

    delivered_orders = orders.filter(
        status='delivered'
    ).count()

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            return redirect('profile')

    else:

        form = ProfileForm(
            instance=request.user
        )

    return render(
        request,
        'accounts/profile.html',
        {
            'form': form,
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
        }
    )