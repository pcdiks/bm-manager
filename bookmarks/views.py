from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django import forms
from .models import Collection, Category, Bookmark
import html.parser

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class NetscapeBookmarkParser(html.parser.HTMLParser):
    """Parser for Netscape Bookmark files with hierarchical structure."""
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_collection = None
        self.current_category = None
        self.current_bookmark = None
        self.last_tag = None
        self.nesting_level = 0  # Track the nesting level of <DL> tags

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.last_tag = tag

        if tag == "dl":
            self.nesting_level += 1  # Entering a new <DL>, increase nesting level
        elif tag == "h3":  # Collection or category
            self.current_bookmark = None  # Reset bookmark
        elif tag == "a":  # Bookmark
            if self.current_category:  # Ensure we have a valid category
                self.current_bookmark = {
                    "url": attrs.get("href", ""),
                    "display_name": None,
                    "notes": None,
                    "category": self.current_category,
                }

    def handle_data(self, data):
        """Handle collection names, category names, bookmark display names, and notes."""
        if self.last_tag == "h3":
            # Skip empty names
            if not data.strip():
                return

            if self.nesting_level == 1:  # Top-level <H3>, it's a collection
                self.current_collection, _ = Collection.objects.get_or_create(
                    name=data.strip(),
                    owner=self.user,
                    defaults={"description": "Imported from a bookmark file."}
                )
                self.current_category = None  # Reset category for a new collection
                print(f"Created Collection: {self.current_collection}")
            elif self.nesting_level == 2:  # Nested <H3>, it's a category
                if self.current_collection:
                    self.current_category, _ = Category.objects.get_or_create(
                        name=data.strip(),
                        collection=self.current_collection
                    )
                    print(f"Created Category: {self.current_category}")
        elif self.last_tag == "a" and self.current_bookmark:  # Bookmark display name
            self.current_bookmark["display_name"] = data.strip()
            print(f"Set Bookmark Name: {self.current_bookmark['display_name']}")
        elif self.last_tag == "dd" and self.current_bookmark:  # Notes for the bookmark
            self.current_bookmark["notes"] = data.strip()
            print(f"Set Bookmark Notes: {self.current_bookmark['notes']}")

    def handle_endtag(self, tag):
        """Finalize bookmark or handle exiting <DL>."""
        if tag == "a" and self.current_bookmark:
            # Save the bookmark to the database
            Bookmark.objects.create(
                url=self.current_bookmark["url"],
                display_name=self.current_bookmark["display_name"],
                notes=self.current_bookmark["notes"],
                category=self.current_category
            )
            print(f"Saved Bookmark: {self.current_bookmark}")
            self.current_bookmark = None  # Reset for the next bookmark
        elif tag == "dl":
            self.nesting_level -= 1  # Exiting a <DL>, decrease nesting level
            if self.nesting_level < 2:  # Exiting a collection's <DL>, reset category
                self.current_category = None
            if self.nesting_level < 1:  # Exiting the top-level <DL>, reset collection
                self.current_collection = None
                            
@login_required
def home(request):
    collections = Collection.objects.filter(owner=request.user)
    selected_collection_id = request.GET.get('collection')
    selected_collection = get_object_or_404(Collection, id=selected_collection_id) if selected_collection_id else collections.first()
    categories = Category.objects.filter(collection=selected_collection) if selected_collection else []

    # Prepare categories with bookmarks
    categories_with_bookmarks = [
        {
            'category': category,
            'bookmarks': Bookmark.objects.filter(category=category)
        }
        for category in categories
    ]

    return render(request, 'home.html', {
        'collections': collections,
        'selected_collection': selected_collection,
        'categories_with_bookmarks': categories_with_bookmarks,
    })

@login_required
def collection_list(request):
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'bookmarks/collection_list.html', {'collections': collections})

@login_required
def collection_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:  # Validate that the 'name' field is not empty
            Collection.objects.create(name=name, description=description, owner=request.user)
            return JsonResponse({'success': True})  # Indicate success for AJAX

        # If validation fails, render the form HTML and return it
        form_html = render_to_string(
            'bookmarks/partials/collection_form.html',
            {'name': name, 'description': description},
            request=request
        )
        return JsonResponse({'success': False, 'html': form_html}, status=400)

    # If not POST, return an error for invalid request methods
    return JsonResponse({'error': 'Invalid request method'}, status=405)
        
@login_required
def collection_update(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if collection.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        collection.name = request.POST.get('name')
        collection.description = request.POST.get('description')
        collection.save()
        return redirect('collection_list')
    return render(request, 'bookmarks/collection_form.html', {'collection': collection})

@login_required
def collection_delete(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if collection.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        collection.delete()
        return redirect('collection_list')
    return render(request, 'bookmarks/collection_confirm_delete.html', {'collection': collection})

@login_required
def category_list(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    categories = Category.objects.filter(collection=collection)
    return render(request, 'bookmarks/category_list.html', {'categories': categories, 'collection': collection})

@login_required
def category_create(request, collection_id):
    # Ensure the user has access to the collection
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')

        if name:  # Validate that the 'name' field is not empty
            Category.objects.create(name=name, collection=collection)
            return JsonResponse({'success': True})  # Indicate success for AJAX

        # If validation fails, render the form HTML and return it
        form_html = render_to_string(
            'bookmarks/partials/category_form.html',
            {'name': name},
            request=request
        )
        return JsonResponse({'success': False, 'html': form_html}, status=400)

    # If not POST, return an error for invalid request methods
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def category_update(request, collection_id, category_id):
    category = get_object_or_404(Category, id=category_id, collection__id=collection_id, collection__owner=request.user)

    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        if category.name:
            category.save()
            return JsonResponse({'success': True})  # Respond for AJAX requests
        return JsonResponse({'success': False, 'error': 'Category name cannot be empty.'}, status=400)

    return JsonResponse({'name': category.name})

@login_required
def category_delete(request, collection_id, category_id):
    category = get_object_or_404(Category, id=category_id, collection__id=collection_id, collection__owner=request.user)

    if request.method == 'POST':
        category.delete()
        return JsonResponse({'success': True})  # Respond for AJAX requests

    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@login_required
def bookmark_list(request, collection_id, category_id):
    category = get_object_or_404(Category, id=category_id, collection__id=collection_id, collection__owner=request.user)
    bookmarks = Bookmark.objects.filter(category=category)
    return render(request, 'bookmarks/bookmark_list.html', {'bookmarks': bookmarks, 'category': category})


@login_required
def bookmark_create(request, collection_id, category_id):
    # Ensure the user has access to the collection and category
    category = get_object_or_404(Category, id=category_id, collection__id=collection_id, collection__owner=request.user)
    
    if request.method == 'POST':
        url = request.POST.get('url')
        display_name = request.POST.get('display_name')
        notes = request.POST.get('notes')
        tags = request.POST.get('tags')  # Comma-separated tags

        if url and display_name:  # Ensure required fields are present
            Bookmark.objects.create(
                url=url,
                display_name=display_name,
                notes=notes,
                tags=tags,
                category=category
            )
            return JsonResponse({'success': True})  # Indicate success for AJAX

        # If validation fails, render the form HTML and return it
        form_html = render_to_string(
            'bookmarks/partials/bookmark_form.html',
            {'url': url, 'display_name': display_name, 'notes': notes, 'tags': tags},
            request=request
        )
        return JsonResponse({'success': False, 'html': form_html}, status=400)

    # If not POST, show the bookmark creation form (not typically used in AJAX)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def bookmark_update(request, collection_id, category_id, pk):
    bookmark = get_object_or_404(Bookmark, id=pk, category__id=category_id, category__collection__id=collection_id, category__collection__owner=request.user)
    if request.method == 'POST':
        bookmark.url = request.POST.get('url')
        bookmark.display_name = request.POST.get('display_name')
        bookmark.notes = request.POST.get('notes')
        bookmark.tags = request.POST.get('tags')  # Comma-separated tags
        bookmark.save()
        return redirect('bookmark_list', collection_id=collection_id, category_id=category_id)
    return render(request, 'bookmarks/bookmark_form.html', {'bookmark': bookmark})

@login_required
def bookmark_edit(request, collection_id, category_id, pk):
    bookmark = get_object_or_404(
        Bookmark,
        id=pk,
        category__id=category_id,
        category__collection__id=collection_id,
        category__collection__owner=request.user,
    )
    if request.method == 'POST':
        # Update the bookmark with form data
        bookmark.url = request.POST.get('url')
        bookmark.display_name = request.POST.get('display_name')
        bookmark.notes = request.POST.get('notes')
        bookmark.tags = request.POST.get('tags')
        bookmark.save()
        return JsonResponse({'success': True})

    # Render the partial template for the edit form
    return render(request, 'bookmarks/partials/bookmark_form.html', {'bookmark': bookmark})

@login_required
def bookmark_delete(request, collection_id, category_id, pk):
    bookmark = get_object_or_404(
        Bookmark,
        id=pk,
        category__id=category_id,
        category__collection__id=collection_id,
        category__collection__owner=request.user,
    )
    if request.method == 'POST':
        bookmark.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def account(request):
    """Account overview page."""
    return render(request, 'account/account.html')

@login_required
def change_password(request):
    """Change the user's password."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            return redirect('account')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})

@login_required
def delete_account(request):
    """Delete the user's account."""
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'account/delete_account.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # Log the user in after successful registration
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def import_bookmarks(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("bookmark_file")
        if uploaded_file:
            try:
                # Read and parse the uploaded file
                parser = NetscapeBookmarkParser(request.user)
                parser.feed(uploaded_file.read().decode("utf-8"))
                messages.success(request, "Bookmarks imported successfully!")
            except Exception as e:
                messages.error(request, f"Failed to import bookmarks: {e}")
        else:
            messages.error(request, "No file uploaded.")
        return redirect("account")
    return render(request, "account/import_bookmarks.html")