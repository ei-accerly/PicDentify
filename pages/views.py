from django.shortcuts import render, redirect, reverse
from django.core import serializers
from django.views.generic import TemplateView
from .models import AdminUser, AdminKey, Topics, Difficulty
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.core.cache import cache
import random, string, requests, json
from django.forms.models import model_to_dict
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import wordnet

# initialize WordNet
nltk.download('wordnet')


@login_required
def protected_view(request):
    # Your protected view logic here
    return render(request, 'loginPage.html')

def logout_view(request):
    logout(request)
    return redirect('/')
# Create your views here.
class TryView(TemplateView):
    template_name = 'try.html'
    def post(self, request):
        if request.POST.get('search_term'):
            
            # Get the search term from the POST request
            search_term = request.POST.get('search_term', '')
            
            url = f"https://www.merriam-webster.com/thesaurus/{search_term}"
            response = requests.get(url)
            html_content = response.content

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the element that contains the synonyms
            share_link = soup.find('a', class_='fb share-link')

            # Extract the synonyms from the data-share-description attribute
            if share_link:
                synonyms_str, antonyms_str = share_link.get('data-share-description', ''), ''
                if 'Antonyms of' in synonyms_str:
                    synonyms_str, antonyms_str = synonyms_str.split(';')
                synonyms_list = [s.strip() for s in synonyms_str.split(':')[1].split(',')]
                antonyms_list = [s.strip() for s in antonyms_str.split(':')[1].split(',')] if antonyms_str else []
                print('Synonyms:', synonyms_list)
                print('Antonyms:', antonyms_list)
            return render(request, 'try.html', {'results': synonyms_list, 'antonyms':antonyms_list})
        
        # Render the search form if the request method is not POST
       
class LoginPage(TemplateView):
    template_name = 'loginPage.html'
    def get(self, request):
        try:
            AdminKey.objects.get(pk=1)
        except:
            AdminKey.objects.create(key_id=1, admin_key="deped143")
        
        admins = AdminUser.objects.all()
        return render(request, 'loginPage.html', {'admins': admins})
    
    def post(self, request):
        def generate_random_string():
            characters = string.ascii_letters + string.digits
            teacher_key = ''.join(random.choice(characters) for i in range(8))
            try:
                if AdminUser.objects.get(user_key=teacher_key):
                    generate_random_string()
            except:
                return teacher_key

        if request.POST.get('admin_key'):
            admin_key_input = request.POST['admin_key']
            check_admin_key = AdminKey.objects.get(pk=1)

            if admin_key_input == check_admin_key.admin_key:
                return JsonResponse({'adminKeyVerify': True})

            else:
               return JsonResponse({'adminKeyVerify': False})
        elif request.POST.get('new_user_hidden'):
            teacher_key = generate_random_string()
            if request.POST['password'] == request.POST['password1']:
                admins = AdminUser.objects.all()

                admin_user = AdminUser.objects.create_superuser(admin_id=admins.count()+1, username=request.POST['new_user'], 
                                                   password=request.POST['password'], user_key=teacher_key)
                admin_user.save()
            else:
                messages.success(request, ("Password didn't match!"))	
                return redirect('/')	
        else:
            username = request.POST['existing_user']
            password = request.POST['password_existing']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['username'] = username
                request.session.save()
            return render(request, 'teacherDashboard.html')
            
class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'teacherDashboard.html'

    def get(self, request):
        user = AdminUser.objects.get(username=request.session.get('username'))
        def create_topic(topic_name):
            topics = Topics.objects.all()
            try:
                Topics.objects.get(topic_name=topic_name, owner_id=user.admin_id)
            except:
                if topic_name == "Synonyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1, topic_name=topic_name, owner_id=user.admin_id)
                    topic.save()
                    for i in range(1, 4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "beautiful, huge, perfect, rough, sharp, cruel, many, baby, light, cute"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='easy',
                                            words=word_list, topic_id=topic.topic_id, time_limit=10,
                                            points_per_question=10, maxpoints=100, answered=0)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "ladder, lady, army, employ, garden, clock, late, bought, lunch, wrist"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='medium',
                                            words=word_list, topic_id=topic.topic_id, time_limit=12,
                                            points_per_question=20, maxpoints=200, answered=0)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "health, disappear, newspaper, cardboard, trouble, behind, caught, picnic, shiny, hallway"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='difficult',
                                            words=word_list, topic_id=topic.topic_id, time_limit=15,
                                            points_per_question=30, maxpoints=300, answered=0)
                            difficulty_save.save()

                elif topic_name == "Antonyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1, topic_name=topic_name, owner_id=user.admin_id)
                    topic.save()
                    for i in range(1, 4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "beautiful, huge, perfect, rough, sharp, cruel, many, baby, light, cute"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='easy',
                                                words=word_list, topic_id=topic.topic_id, time_limit=10,
                                                points_per_question=10, maxpoints=100, answered=0)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "ladder, lady, army, employ, garden, clock, late, bought, lunch, wrist"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='medium',
                                                words=word_list, topic_id=topic.topic_id, time_limit=12,
                                                points_per_question=20, maxpoints=200, answered=0)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "health, disappear, newspaper, cardboard, trouble, behind, caught, picnic, shiny, hallway"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='difficult',
                                                words=word_list, topic_id=topic.topic_id, time_limit=15,
                                                points_per_question=30, maxpoints=300, answered=0)
                            difficulty_save.save()
                elif topic_name == "Homonyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1, topic_name=topic_name, owner_id=user.admin_id)
                    topic.save()
                    for i in range(1, 4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "beautiful, huge, perfect, rough, sharp, cruel, many, baby, light, cute"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='easy',
                                            words=word_list, topic_id=topic.topic_id, time_limit=10,
                                            points_per_question=10, maxpoints=100, answered=0)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "ladder, lady, army, employ, garden, clock, late, bought, lunch, wrist"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='medium',
                                            words=word_list, topic_id=topic.topic_id, time_limit=12,
                                            points_per_question=20, maxpoints=200, answered=0)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "health, disappear, newspaper, cardboard, trouble, behind, caught, picnic, shiny, hallway"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='difficult',
                                            words=word_list, topic_id=topic.topic_id, time_limit=15,
                                            points_per_question=30, maxpoints=300, answered=0)
                            difficulty_save.save()
                elif topic_name == "Hyponyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1, topic_name=topic_name, owner_id=user.admin_id)
                    topic.save()
                    for i in range(1, 4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "beautiful, huge, perfect, rough, sharp, cruel, many, baby, light, cute"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='easy',
                                            words=word_list, topic_id=topic.topic_id, time_limit=10,
                                            points_per_question=10, maxpoints=100, answered=0)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "ladder, lady, army, employ, garden, clock, late, bought, lunch, wrist"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='medium',
                                            words=word_list, topic_id=topic.topic_id, time_limit=12,
                                            points_per_question=20, maxpoints=200, answered=0)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "health, disappear, newspaper, cardboard, trouble, behind, caught, picnic, shiny, hallway"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='difficult',
                                            words=word_list, topic_id=topic.topic_id, time_limit=15,
                                            points_per_question=30, maxpoints=300, answered=0)
                            difficulty_save.save()
                elif topic_name == "Homographs":
                    topic = Topics.objects.create(topic_id=topics.count()+1, topic_name=topic_name, owner_id=user.admin_id)
                    topic.save()
                    for i in range(1, 4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "beautiful, huge, perfect, rough, sharp, cruel, many, baby, light, cute"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='easy',
                                            words=word_list, topic_id=topic.topic_id, time_limit=10,
                                            points_per_question=10, maxpoints=100, answered=0)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "ladder, lady, army, employ, garden, clock, late, bought, lunch, wrist"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='medium',
                                            words=word_list, topic_id=topic.topic_id, time_limit=12,
                                            points_per_question=20, maxpoints=200, answered=0)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "health, disappear, newspaper, cardboard, trouble, behind, caught, picnic, shiny, hallway"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name='difficult',
                                            words=word_list, topic_id=topic.topic_id, time_limit=15,
                                            points_per_question=30, maxpoints=300, answered=0)
                            difficulty_save.save()
            
        create_topics = ["Synonyms", "Antonyms", "Homonyms", "Hyponyms", "Homographs"]
        for topic in create_topics:
            create_topic(topic)
        topics = Topics.objects.filter(owner_id=user.admin_id)
        difficulty = Difficulty.objects.all()
        return render(request, 'teacherDashboard.html', {'user_key':user.user_key, 'topics': topics, 'difficulty':difficulty})
    
    def post(self, request):
        user = AdminUser.objects.get(username=request.session.get('username'))
        difficulty = Difficulty.objects.all()

        if request.POST.get('topic_to_edit_samp'):
            difficulties = Difficulty.objects.filter(topic_id=request.POST['topic_to_edit_samp'])
            topic = Topics.objects.get(topic_id=request.POST['topic_to_edit_samp'])

            difficulties_data = []
            for difficulty in difficulties:
                difficulty_dict = model_to_dict(difficulty)
                difficulties_data.append(difficulty_dict)

            # Return a JSON response with both the topic and difficulties data
            return JsonResponse({'topic': topic.topic_name, 'difficulties': difficulties_data})


        elif request.POST.get('addTopic'):
            try:
                isTopic = Topics.objects.get(topic_name=request.POST['addTopic'])
                Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name=request.POST['difficulty'],
                                            words=request.POST['words_list'], topic_id=isTopic.topic_id, time_limit=request.POST['time_limit'],
                                            points_per_question=request.POST['points_per_question'])
            except:
                topics = Topics.objects.all()
                topic = Topics.objects.create(topic_id=topics.count()+1, topic_name=request.POST['addTopic'], owner_id=user.admin_id)
                topic.save()
                Difficulty.objects.create(difficulty_id=difficulty.count()+1, difficulty_name=request.POST['difficulty'],
                                            words=request.POST['words_list'], topic_id=topic.topic_id, time_limit=request.POST['time_limit'],
                                            points_per_question=request.POST['points_per_question'])

            return render(request, 'teacherDashboard.html')
        
        elif request.POST.get('topicPreviousName'):
            isTopic = Topics.objects.get(topic_name=request.POST['topicPreviousName'])
            isTopic.topic_name = request.POST['topicTitle2']
            isTopic.save()
            difficulty = Difficulty.objects.get(difficulty_name=request.POST['topicChange'], topic_id=isTopic.topic_id)

            difficulty.words = request.POST['topicWords2']
            difficulty.points_per_question = request.POST['points_per_question_edit']
            difficulty.time_limit = request.POST['topicDuration2']
            difficulty.save()
    

            return render(request, 'teacherDashboard.html')

class StudentDashboard(TemplateView):
    template_name = 'studentDashboard.html'

    def get(self, request):
        try:
            user = AdminUser.objects.get(username=request.session['username'])
            topics = Topics.objects.filter(owner_id=user.admin_id)
            return render(request, 'studentDashboard.html', {'topics':topics, 'user':user})
        except:

            return redirect('/studentlogin/')
        
    def post(self, request):
        if request.POST.get('difficulty') == 'easy':
            try:
                questions = Difficulty.objects.get(difficulty_name='easy', topic_id=request.POST.get('topic_id'))
                return JsonResponse({'questions': questions.difficulty_id})
            except: 
                return redirect('/studentdashboard/')
        elif request.POST.get('difficulty') == 'medium':
            try:
                questions = Difficulty.objects.get(difficulty_name='medium', topic_id=request.POST.get('topic_id'))
                return JsonResponse({'questions': questions.difficulty_id})
            except: 
                return redirect('/studentdashboard/')
        else:
            try:
                questions = Difficulty.objects.get(difficulty_name='difficult', topic_id=request.POST.get('topic_id'))
                return JsonResponse({'questions': questions.difficulty_id})
            except: 
                return redirect('/studentdashboard/')

class StudentActivity(TemplateView):

    def get(self, request):
        def synonyms_antonyms_list(word, category):
            # Get the HTML content of a web page
            url = f"https://www.merriam-webster.com/thesaurus/{word}"
            response = requests.get(url)
            html_content = response.content

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the element that contains the synonyms and antonyms
            share_link = soup.find('a', class_='fb share-link')

            # Extract the synonyms and antonyms from the data-share-description attribute
            if share_link:
                synonyms_str, antonyms_str = share_link.get('data-share-description', ''), ''
                if 'Antonyms of' in synonyms_str:
                    synonyms_str, antonyms_str = synonyms_str.split(';')
                synonyms_list = [s.strip() for s in synonyms_str.split(':')[1].split(',')]
                antonyms_list = [s.strip() for s in antonyms_str.split(':')[1].split(',')] if antonyms_str else []
                if category == 1:
                    return synonyms_list
                elif category == 2:
                    return antonyms_list
                elif category == 3:
                    return word
                elif category == 4:
                    synsets = wordnet.synsets(word)
                    hyponyms = []
                    for synset in synsets:
                        for hyponym in synset.hyponyms():
                            hyponyms.append(hyponym.name().split('.')[0])
                    return hyponyms[:7]
                else:
                    synsets = wordnet.synsets(word)
    
                    # Keep only synsets that have more than one lemma
                    synsets = [s for s in synsets if len(s.lemmas()) > 1]
                    
                    # Get all lemmas for each synset and extract homographs
                    homographs = set()
                    for s in synsets:
                        for l in s.lemmas():
                            if l.name() != word:
                                homographs.add(l.name())
                    
                    # Return list of homographs
                    return list(homographs)
        def fetch_words():
            response = requests.get('https://random-word-api.herokuapp.com/word')
            if response.status_code == 200:
                word = response.json()[0]
                return word
            else:
                print('Error fetching word')

        def fetch_image(query):
            url = f'https://api.unsplash.com/photos/random/?count=5&query={query}&client_id=tl59FZ7ave-tfL1BOjZMfKxACAF1QFglZyc2O-SMbg8'
            # replace YOUR_ACCESS_KEY with your actual Unsplash API access key
            response = requests.get(url)
            image_urls = []
            if response.status_code == 200:
                data = response.json()
                for image_data in data:
                    image_url = image_data['urls']['regular']
                    image_urls.append(image_url)
                return image_urls
            else:
                image_urls.append("no image")
                return image_urls
        
        csrf_token = request.META.get('HTTP_COOKIE', '').split(';')
        questions = Difficulty.objects.get(difficulty_id=csrf_token[0])
        topic_name = Topics.objects.get(topic_id=questions.topic_id)
        words = questions.words.split(',')

        cleaned_words = [word.strip() for word in words]

        persistent_variable = cache.get('my_persistent_variable')
        
        # If the persistent variable doesn't exist yet, initialize it
        if persistent_variable is None:
            persistent_variable = 0
            cache.set('my_persistent_variable', persistent_variable)
        if len(words) == questions.answered:
            if topic_name.topic_name == "Synonyms":
                word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 1)
            elif topic_name.topic_name == "Antonyms":
                word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 2)
            elif topic_name.topic_name == "Homonyms":
                word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 3)
            elif topic_name.topic_name == "Hyponyms":
                word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 4)
            elif topic_name.topic_name == "Homographs":
                word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 5)
            fetch_word = random.randint(0, len(word_list)-1)
            image_url = fetch_image(word_list[fetch_word])
            if (len(image_url) == 0):
                image_url.append("no image")
            choices = []
            for i in range(3):
                choices.append(fetch_words())
            choices.append(cleaned_words[questions.answered-1])
            random.shuffle(choices)
            try:
                random_number = random.randint(0, len(image_url)-1)
            except:
                random_number = 0
            
            return render(request, 'studentActivity.html', {'questions':questions, 'words': cleaned_words[questions.answered-1], 'start_index':questions.answered,
                                                         'img_url':image_url[random_number], 'length':len(words), 'choices':choices, 'answered':'done'})
        # Increment the persistent variable
        persistent_variable = questions.answered + 1
        cache.set('my_persistent_variable', persistent_variable)
        if topic_name.topic_name == "Synonyms":
            word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 1)
        elif topic_name.topic_name == "Antonyms":
            word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 2)
        elif topic_name.topic_name == "Homonyms":
            word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 3)
        elif topic_name.topic_name == "Hyponyms":
            word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 4)
        elif topic_name.topic_name == "Homographs":
            word_list = synonyms_antonyms_list(cleaned_words[persistent_variable-1], 5)
        fetch_word = random.randint(0, len(word_list)-1)
        image_url = fetch_image(word_list[fetch_word])
        if (len(image_url) == 0):
            image_url.append("no image")
        choices = []
        for i in range(3):
            choices.append(fetch_words())
        choices.append(cleaned_words[persistent_variable-1])
        random.shuffle(choices)
        try:
            random_number = random.randint(0, len(image_url)-1)
        except:
            random_number = 0
        return render(request, 'studentActivity.html', {'questions':questions, 'words': cleaned_words[persistent_variable-1], 'start_index':persistent_variable,
                                                         'img_url':image_url[random_number], 'length':len(words), 'choices':choices, 'word_list':word_list})
    def post(self, request):
        if request.POST.get('choice'):
            persistent_variable = cache.get('my_persistent_variable')
            csrf_token = request.META.get('HTTP_COOKIE', '').split(';')
            questions = Difficulty.objects.get(difficulty_id=csrf_token[0])
            words = questions.words.split(',')

            cleaned_words = [word.strip() for word in words]
            

            if request.POST.get('choice') not in cleaned_words:
                return JsonResponse({'answerVerify': False, 'correct_answer':cleaned_words[persistent_variable-1]})
            else:
                return JsonResponse({'answerVerify': True, 'points_per_question':questions.points_per_question})
        else:
            if request.POST.get('isCorrect') == "correct":
                csrf_token = request.META.get('HTTP_COOKIE', '').split(';')
                questions = Difficulty.objects.get(difficulty_id=csrf_token[0])
                questions.score = questions.score + questions.points_per_question
                questions.answered = questions.answered + 1
                questions.save()
            else:
                csrf_token = request.META.get('HTTP_COOKIE', '').split(';')
                questions = Difficulty.objects.get(difficulty_id=csrf_token[0])
                questions.answered = questions.answered + 1
                questions.save()

class StudentLogin(TemplateView):
    template_name = 'studentLogin.html'

    def post(self, request):
        if request.POST.get('admin_key'):
            try:
                admin_user = AdminUser.objects.get(user_key=request.POST['admin_key'])
                username = admin_user.username
                password = admin_user.password
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    request.session['username'] = username
                    request.session.save()
                return JsonResponse({'adminKeyVerify': True})
            except:
                return JsonResponse({'adminKeyVerify': False})


class TopicPage(TemplateView):
    template_name = 'topicPage.html'
