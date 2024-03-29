from django.shortcuts import render,redirect,reverse
from django.core import serializers
from django.views.generic import TemplateView
from .models import AdminUser,AdminKey,Topics,Difficulty,Pictures,Choices
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,authenticate,login
from django.core.cache import cache
import random,string,requests,json,asyncio
from django.forms.models import model_to_dict
from bs4 import BeautifulSoup
import nltk,os,glob,shutil
from nltk.corpus import wordnet
from django.conf import settings
from django.core.files.storage import default_storage

# initialize WordNet
# nltk.download('wordnet')
media_root = settings.MEDIA_ROOT
media_url = settings.MEDIA_URL


@login_required
def protected_view(request):
    # Your protected view logic here
    return render(request,'loginPage.html')

def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('/')
# Create your views here.
class LoginPage(TemplateView):
    template_name = 'loginPage.html'
    def get(self,request):
        try:
            AdminKey.objects.get(pk=1)
        except:
            AdminKey.objects.create(key_id=1,admin_key="deped143")

        admins = AdminUser.objects.all()
        return render(request,'loginPage.html',{'admins': admins})

    def post(self,request):
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

                admin_user = AdminUser.objects.create_superuser(admin_id=admins.count()+1,username=request.POST['new_user'],
                                                   password=request.POST['password'],user_key=teacher_key)
                admin_user.save()
            else:
                messages.success(request,("Password didn't match!"))
                return redirect('/')
        else:
            username = request.POST['existing_user']
            password = request.POST['password_existing']
            user = authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                request.session['username'] = username
                request.session.save()
            return render(request,'teacherDashboard.html')

class Dashboard(LoginRequiredMixin,TemplateView):
    template_name = 'teacherDashboard.html'
    def get(self,request):
        user = AdminUser.objects.get(username=request.session.get('username'))
        def create_topic(topic_name):
            topics = Topics.objects.all()
            try:
                Topics.objects.get(topic_name=topic_name,owner_id=user.admin_id)
            except:
                if topic_name == "Synonyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1,topic_name=topic_name,owner_id=user.admin_id)
                    topic.save()
                    for i in range(1,4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "Big,Kids,Quiet,Small,Quick,Happy,Mad,Rich,Cap,Beautiful"
                            synonyms = "Huge,Children,Silent,Tiny,Fast,Glad,Angry,Wealthy,Hat,Pretty"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='easy',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=10,maxpoints=100,answered=0,words1=synonyms)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "Stone,Wet,Neat,Thin,Cold,Sick,Alike"
                            synonyms = "Pebble,Damp,Tidy,Skinny,Freezing,Ill,Similar"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='medium',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=20,maxpoints=140,answered=0,words1=synonyms)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "Done,Funny,Laugh,Build,Smart"
                            synonyms = "Finished,Silly,Chuckle,Construct,Clever"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='difficult',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=30,maxpoints=150,answered=0,words1=synonyms)
                            difficulty_save.save()

                elif topic_name == "Antonyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1,topic_name=topic_name,owner_id=user.admin_id)
                    topic.save()
                    for i in range(1,4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "Rich,Noisy,Big,Happy,Fast,Walk,Hot,Wet,Open,Day,Beautiful,Long,Good"
                            antonyms = "Poor,Quiet,Small,Sad,Slow,Run,Cold,Dry,Close,Night,Ugly,Short,Bad"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='easy',
                                                words=word_list,topic_id=topic.topic_id,points_per_question=10,maxpoints=100,answered=0,words1=antonyms)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "Start,Top,Strong,Empty,Present,New,Late"
                            antonyms = "Finish,Bottom,Weak,Full,Absent,Old,Early"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='medium',
                                                words=word_list,topic_id=topic.topic_id,points_per_question=20,maxpoints=140,answered=0,words1=antonyms)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "Adult,Build,Friend,First,Correct"
                            antonyms = "Child,Destroy,Enemy,Last,Wrong"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='difficult',
                                                words=word_list,topic_id=topic.topic_id,points_per_question=30,maxpoints=150,answered=0,words1=antonyms)
                            difficulty_save.save()
                elif topic_name == "Homonyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1,topic_name=topic_name,owner_id=user.admin_id)
                    topic.save()
                    for i in range(1,4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "Write,Sea,Sun,Cat,Cup,Deer,Eye,Pail,Mail,Lip"
                            homonyms = "Right,See,Son,Cut,Cop,Dear,I,Pale,Male,Leap"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='easy',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=10,maxpoints=100,answered=0,words1=homonyms)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "Knight,Flower,Dye,Hi,Whole,Eight,One"
                            homonyms = "Night,Flour,Die,High,Hole,Ate,Won"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='medium',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=20,maxpoints=140,answered=0,words1=homonyms)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "Waist,Peace,Heel,Hair,Sent"
                            homonyms = "Waste,Piece,Heal,Hare,Cent"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='difficult',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=30,maxpoints=150,answered=0,words1=homonyms)
                            difficulty_save.save()
                elif topic_name == "Hyponyms":
                    topic = Topics.objects.create(topic_id=topics.count()+1,topic_name=topic_name,owner_id=user.admin_id)
                    topic.save()
                    for i in range(1,4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "Fruits,Colors,Numbers,Tree,Vegetables,Subjects,Planets,Animals,Plants,Insects"
                            hyponyms = "Fruits,Colors,Numbers,Tree,Vegetables,Subjects,Planets,Animals,Plants,Insects"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='easy',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=10,maxpoints=100,answered=0,words1=hyponyms)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "Body Parts,Toys,Drinks,Months,Days,Footwear,Desserts"
                            hyponyms = "Body Parts,Toys,Drinks,Months,Days,Footwear,Desserts"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='medium',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=20,maxpoints=140,answered=0,words1=hyponyms)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "Gadgets,Emotions,Appliances,Vehicles,Fundamental Operations"
                            hyponyms = "Gadgets,Emotions,Appliances,Vehicles,Fundamental Operations"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='difficult',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=30,maxpoints=150,answered=0,words1=hyponyms)
                            difficulty_save.save()
                elif topic_name == "Homographs":
                    topic = Topics.objects.create(topic_id=topics.count()+1,topic_name=topic_name,owner_id=user.admin_id)
                    topic.save()
                    for i in range(1,4):
                        difficulty = Difficulty.objects.all()
                        if i == 1:
                            word_list = "Bat,Watch,Letter,Fly,Nail,Ring,Ship,Tie,Left,Right"
                            homographs = "Bat,Watch,Letter,Fly,Nail,Ring,Ship,Tie,Left,Right"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='easy',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=10,maxpoints=100,answered=0,words1=homographs)
                            difficulty_save.save()
                        elif i == 2:
                            word_list = "Palm,Trunk,Rock,Sink,Park, Bark,Wave"
                            homographs = "Palm,Trunk,Rock,Sink,Park, Bark,Wave"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='medium',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=20,maxpoints=140,answered=0,words1=homographs)
                            difficulty_save.save()
                        elif i == 3:
                            word_list = "Can,Tear,Bow,Bank,Band"
                            homographs = "Can,Tear,Bow,Bank,Band"
                            difficulty_save = Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name='difficult',
                                            words=word_list,topic_id=topic.topic_id,points_per_question=30,maxpoints=150,answered=0,words1=homographs)
                            difficulty_save.save()

        create_topics = ["Synonyms","Antonyms","Homonyms","Hyponyms","Homographs"]
        for topic in create_topics:
            create_topic(topic)
        topics = Topics.objects.filter(owner_id=user.admin_id)
        difficulty = Difficulty.objects.all()
        return render(request,'teacherDashboard.html',{'user_key':user.user_key,'topics': topics,'difficulty':difficulty})

    def post(self,request):
        user = AdminUser.objects.get(username=request.session.get('username'))
        difficulty = Difficulty.objects.all()

        if request.POST.get('save_changes'):
            difficulties = Difficulty.objects.get(difficulty_id=request.POST['topicId'])
            difficulty_words = difficulties.words.split(",")
            difficulty_words_length = len(difficulty_words)
            difficulties.points_per_question = request.POST['points_per_question_edit']
            difficulties.maxpoints = int(request.POST['points_per_question_edit']) * int(difficulty_words_length)
            difficulties.save()

            try:
                choices = Choices.objects.get(difficulty_id=request.POST['topicId'],choices_name=request.POST['difficultyWord1'])
                choices_input = request.POST['word_choices1']
                choices.word_choices = choices_input
                choices.save()
            except:
                choices = Choices.objects.all()
                choices_input = request.POST['word_choices1']
                choices_save = Choices.objects.create(choices_id=len(choices)+1,choices_name=request.POST['difficultyWord1'],word_choices=choices_input,difficulty_id=request.POST['topicId'])
                choices_save.save()

            try:
                choices1 = Choices.objects.get(difficulty_id=request.POST['topicId'],choices_name=request.POST['difficultyWord2'])
                choices_input1 = request.POST['word_choices2']
                choices1.word_choices = choices_input1
                choices1.save()

            except:
                choices1 = Choices.objects.all()
                choices_input1 = request.POST['word_choices2']
                choices_save1 = Choices.objects.create(choices_id=len(choices1)+1,choices_name=request.POST['difficultyWord2'],word_choices=choices_input1,difficulty_id=request.POST['topicId'])
                choices_save1.save()

            return JsonResponse({'doneSave': True})

        elif request.POST.get('topic_to_edit_samp'):

            difficulties = Difficulty.objects.filter(topic_id=request.POST['topic_to_edit_samp'])
            topic = Topics.objects.get(topic_id=request.POST['topic_to_edit_samp'])
            easy_difficulty = Difficulty.objects.get(topic_id=request.POST['topic_to_edit_samp'],difficulty_name="easy")
            easy_difficulty_split = easy_difficulty.words.split(",")
            easy1_difficulty_split = easy_difficulty.words1.split(",")


            image_urls = []
            for filename in os.listdir(media_root):
                if easy_difficulty_split[0] == os.path.splitext(filename)[0][:-1]:
                    image_path = os.path.join(media_url,filename)
                    image_urls.append(image_path)
            if topic.topic_name != "Homographs":
                image_urls1 = []
                for filename in os.listdir(media_root):
                    if easy1_difficulty_split[0] == os.path.splitext(filename)[0][:-1]:
                        image_path1 = os.path.join(media_url,filename)
                        image_urls1.append(image_path1)
            else:
                image_urls1 = []
                for filename in os.listdir(media_root):
                    if "HG"+easy1_difficulty_split[0] == os.path.splitext(filename)[0][:-1]:
                        image_path1 = os.path.join(media_url,filename)
                        image_urls1.append(image_path1)

            difficulties_data = []
            for difficulty in difficulties:
                difficulty_dict = model_to_dict(difficulty)
                difficulties_data.append(difficulty_dict)
            try:
                choices = Choices.objects.get(difficulty_id=easy_difficulty.difficulty_id,choices_name=easy_difficulty_split[0])
                choices_split = choices.word_choices.split(",")

            except:
                choices_split = ""

            try:
                choices1 = Choices.objects.get(difficulty_id=easy_difficulty.difficulty_id,choices_name=easy1_difficulty_split[0])
                choices_split1 = choices1.word_choices.split(",")

            except:
                choices_split1 = ""
            # Return a JSON response with both the topic and difficulties data
            return JsonResponse({'topic': topic.topic_name,'difficulties': difficulties_data,'image':image_urls,'image1':image_urls1,'choices':choices_split, 'choices1':choices_split1})


        elif request.POST.get('addTopic'):
            try:
                isTopic = Topics.objects.get(topic_name=request.POST['addTopic'])
                Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name=request.POST['difficulty'],
                                            words=request.POST['words_list'],topic_id=isTopic.topic_id,points_per_question=request.POST['points_per_question'])
            except:
                topics = Topics.objects.all()
                topic = Topics.objects.create(topic_id=topics.count()+1,topic_name=request.POST['addTopic'],owner_id=user.admin_id)
                topic.save()
                Difficulty.objects.create(difficulty_id=difficulty.count()+1,difficulty_name=request.POST['difficulty'],
                                            words=request.POST['words_list'],topic_id=topic.topic_id,points_per_question=request.POST['points_per_question'])

            return render(request,'teacherDashboard.html')

        elif request.POST.get('fetch_picture'):
            isTopic = Topics.objects.get(topic_name=request.POST['topic_to_get'])
            difficulty = Difficulty.objects.get(difficulty_name=request.POST['difficulty_to_get'],topic_id=isTopic.topic_id)

            image_urls = []
            for filename in os.listdir(media_root):
                if request.POST.get('fetch_picture').replace(" ","") == os.path.splitext(filename)[0][:-1]:
                    image_path = os.path.join(media_url,filename)
                    image_urls.append(image_path)

            if difficulty.topic.topic_name != "Homographs":
                image_urls1 = []
                for filename in os.listdir(media_root):
                    if request.POST.get('fetch_picture1').replace(" ","") == os.path.splitext(filename)[0][:-1]:
                        image_path1 = os.path.join(media_url,filename)
                        image_urls1.append(image_path1)
            else:
                image_urls1 = []
                for filename in os.listdir(media_root):
                    if "HG"+request.POST.get('fetch_picture1').replace(" ","") == os.path.splitext(filename)[0][:-1]:
                        image_path1 = os.path.join(media_url,filename)
                        image_urls1.append(image_path1)

            try:
                choices = Choices.objects.get(difficulty_id=difficulty.difficulty_id,choices_name=request.POST.get('fetch_picture'))
                choices_split = choices.word_choices.split(",")

            except:
                choices_split = ""

            try:
                choices1 = Choices.objects.get(difficulty_id=difficulty.difficulty_id,choices_name=request.POST.get('fetch_picture1'))
                choices_split1 = choices1.word_choices.split(",")

            except:
                choices_split1 = ""

            return JsonResponse({'images':image_urls,'images1':image_urls1,'choices':choices_split, 'choices1':choices_split1})

        elif request.POST.get('word'):
            for filename in os.listdir(media_root):
                if request.POST['word'] == os.path.splitext(filename)[0]:
                    print(os.path.splitext(filename)[0])
                    file_path = os.path.join(settings.MEDIA_ROOT,filename)
                    os.remove(file_path)
                    break

      
            uploaded_file = request.FILES['picture-' + request.POST['imagePos']]
            file_path = default_storage.save(uploaded_file.name,uploaded_file)

         

            new_file_name = request.POST['word'] + os.path.splitext(file_path)[1]  
            full_file_path = os.path.join(settings.MEDIA_ROOT,file_path)
     
            new_full_file_path = os.path.join(settings.MEDIA_ROOT,new_file_name)



            os.rename(full_file_path,new_full_file_path)

            return JsonResponse({'imageChange': True})

        elif request.POST.get('addAWord'):
            difficulty = Difficulty.objects.get(difficulty_id=request.POST['topicIdToBeAdded'])
            if difficulty.topic.topic_name != "Homographs" and difficulty.topic.topic_name != "Hyponyms":
                difficulty.words = difficulty.words + "," +request.POST['add_word1']
                difficulty.words1 = difficulty.words1 + "," +request.POST['add_word2']
                difficulty.save()
                difficulty_nextquery = Difficulty.objects.get(difficulty_id=request.POST['topicIdToBeAdded'])
                difficulty_words = difficulty_nextquery.words.split(",")
                difficulty_words_length = len(difficulty_words)
                difficulty_nextquery.maxpoints = int(difficulty_nextquery.points_per_question) * int(difficulty_words_length)
                difficulty_nextquery.save()
            else:
                difficulty.words = difficulty.words + "," +request.POST['add_word1']
                difficulty.words1 = difficulty.words1 + "," +request.POST['add_word1']
                difficulty.save()
                difficulty_nextquery = Difficulty.objects.get(difficulty_id=request.POST['topicIdToBeAdded'])
                difficulty_words = difficulty_nextquery.words.split(",")
                difficulty_words_length = len(difficulty_words)
                difficulty_nextquery.maxpoints = int(difficulty_nextquery.points_per_question) * int(difficulty_words_length)
                difficulty_nextquery.save()
            return render(request,'teacherDashboard.html')

        elif request.POST.get("wordToEdit"):
            wordToEdit = False
            difficulty_check_all = Difficulty.objects.all()
            for difficulty_check in difficulty_check_all:
                if difficulty_check.topic.topic_name == "Synonyms":
                    words = difficulty_check.words.split(",")
                    if request.POST['inputField'] in words:
                        wordToEdit = True
                        break
                else:
                    words = difficulty_check.words.split(",")
                    words1 = difficulty_check.words1.split(",")
                    if request.POST['inputField'] in words or request.POST['inputField'] in words1:
                        wordToEdit = True
                        break

            difficulty = Difficulty.objects.get(difficulty_id=request.POST['topicIdWord1Edit'])
            if difficulty.topic.topic_name == "Homographs" or difficulty.topic.topic_name == "Hyponyms":
                difficulty.words = difficulty.words.replace(request.POST["wordToEdit"], request.POST["inputField"])
                difficulty.words1 = difficulty.words1.replace(request.POST["wordToEdit"], request.POST["inputField"])
                difficulty.save()
            else:
                difficulty.words = difficulty.words.replace(request.POST["wordToEdit"], request.POST["inputField"])
                difficulty.save()

            for filename in os.listdir(media_root):
                if request.POST["inputField"] == os.path.splitext(filename)[0][:-1]:
                    wordToEdit == True
                    break

            if wordToEdit == False:
                difficulty_check_all = Difficulty.objects.all()
                for difficulty_check in difficulty_check_all:
                    if difficulty_check.topic.topic_name == "Synonyms":
                        words = difficulty_check.words.split(",")
                        if request.POST['wordToEdit'] in words:
                            for filename in os.listdir(media_root):
                                if request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                                    new_filename = filename.replace(request.POST["wordToEdit"], request.POST["inputField"])
                                    new_filepath = os.path.join(media_root, new_filename)
                                    image_path = os.path.join(media_root,filename)
                                    try:
                                        shutil.copy(image_path, new_filepath)
                                    except (IOError, OSError) as e:
                                        print(f"Error copying file: {e}")
                                if difficulty.topic.topic_name == "Homographs":
                                    if "HG"+request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                                        new_filename = filename.replace("HG"+request.POST["wordToEdit"], "HG"+request.POST["inputField"])
                                        new_filepath = os.path.join(media_root, new_filename)
                                        image_path = os.path.join(media_root,filename)
                                        try:
                                            shutil.copy(image_path, new_filepath)
                                        except (IOError, OSError) as e:
                                            print(f"Error copying file: {e}")
                            break
                    else:
                        words = difficulty_check.words.split(",")
                        words1 = difficulty_check.words1.split(",")
                        if request.POST['wordToEdit'] in words or request.POST['wordToEdit'] in words1:
                            for filename in os.listdir(media_root):
                                if request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                                    new_filename = filename.replace(request.POST["wordToEdit"], request.POST["inputField"])
                                    new_filepath = os.path.join(media_root, new_filename)
                                    image_path = os.path.join(media_root,filename)
                                    try:
                                        shutil.copy(image_path, new_filepath)
                                    except (IOError, OSError) as e:
                                        print(f"Error copying file: {e}")
                                if difficulty.topic.topic_name == "Homographs":
                                    if "HG"+request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                                        new_filename = filename.replace("HG"+request.POST["wordToEdit"], "HG"+request.POST["inputField"])
                                        new_filepath = os.path.join(media_root, new_filename)
                                        image_path = os.path.join(media_root,filename)
                                        try:
                                            shutil.copy(image_path, new_filepath)
                                        except (IOError, OSError) as e:
                                            print(f"Error copying file: {e}")
                            break
            pictureIsDelete = False
            difficulty_check_all = Difficulty.objects.all()
            for difficulty_check in difficulty_check_all:
                if difficulty_check.topic.topic_name == "Synonyms":
                    words = difficulty_check.words.split(",")
                    if request.POST['wordToEdit'] in words:
                        pictureIsDelete = True
                        break
                else:
                    words = difficulty_check.words.split(",")
                    words1 = difficulty_check.words1.split(",")
                    if request.POST['wordToEdit'] in words or request.POST['wordToEdit'] in words1:
                        pictureIsDelete = True
                        break
            if pictureIsDelete == False:
                for filename in os.listdir(media_root):
                    if request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                        file_path = os.path.join(settings.MEDIA_ROOT,filename)
                        os.remove(file_path)
                    if difficulty.topic.topic_name == "Homographs":
                        if "HG"+request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                            file_path = os.path.join(settings.MEDIA_ROOT,filename)
                            os.remove(file_path)
            return render(request,'teacherDashboard.html')

        elif request.POST.get("wordToEdit1"):
            wordToEdit = False
            difficulty_check_all = Difficulty.objects.all()
            difficulty = Difficulty.objects.get(difficulty_id=request.POST['topicIdWord2Edit'])
            if difficulty.topic.topic_name == "Synonyms":
                difficulty.words1 = difficulty.words1.replace(request.POST["wordToEdit1"], request.POST["inputField2"])
                difficulty.save()

            else:
                for difficulty_check in difficulty_check_all:
                    if difficulty_check.topic.topic_name == "Synonyms":
                        words = difficulty_check.words.split(",")
                        if request.POST['inputField2'] in words:
                            wordToEdit = True
                            break
                    else:
                        words = difficulty_check.words.split(",")
                        words1 = difficulty_check.words1.split(",")
                        if request.POST['inputField2'] in words or request.POST['inputField2'] in words1:
                            wordToEdit = True
                            break
                if difficulty.topic.topic_name == "Homographs" or difficulty.topic.topic_name == "Hyponyms":
                    difficulty.words = difficulty.words.replace(request.POST["wordToEdit1"], request.POST["inputField2"])
                    difficulty.words1 = difficulty.words1.replace(request.POST["wordToEdit1"], request.POST["inputField2"])
                    difficulty.save()
                else:
                    difficulty.words1 = difficulty.words1.replace(request.POST["wordToEdit1"], request.POST["inputField2"])
                    difficulty.save()

                if wordToEdit == False:
                    difficulty_check_all = Difficulty.objects.all()
                    for difficulty_check in difficulty_check_all:
                        if difficulty_check.topic.topic_name == "Synonyms":
                            words = difficulty_check.words.split(",")
                            if request.POST['wordToEdit1'] in words:
                                for filename in os.listdir(media_root):
                                    if request.POST['wordToEdit1'] == os.path.splitext(filename)[0][:-1]:
                                        new_filename = filename.replace(request.POST["wordToEdit1"], request.POST["inputField2"])
                                        new_filepath = os.path.join(media_root, new_filename)
                                        image_path = os.path.join(media_root,filename)
                                        try:
                                            shutil.copy(image_path, new_filepath)
                                        except (IOError, OSError) as e:
                                            print(f"Error copying file: {e}")
                                    if difficulty.topic.topic_name == "Homographs":
                                        if "HG"+request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                                            new_filename = filename.replace("HG"+request.POST["wordToEdit1"], "HG"+request.POST["inputField2"])
                                            new_filepath = os.path.join(media_root, new_filename)
                                            image_path = os.path.join(media_root,filename)
                                            try:
                                                shutil.copy(image_path, new_filepath)
                                            except (IOError, OSError) as e:
                                                print(f"Error copying file: {e}")
                                break
                        else:
                            words = difficulty_check.words.split(",")
                            words1 = difficulty_check.words1.split(",")
                            if request.POST['wordToEdit1'] in words or request.POST['wordToEdit1'] in words1:
                                for filename in os.listdir(media_root):
                                    if request.POST['wordToEdit1'] == os.path.splitext(filename)[0][:-1]:
                                        new_filename = filename.replace(request.POST["wordToEdit1"], request.POST["inputField2"])
                                        new_filepath = os.path.join(media_root, new_filename)
                                        image_path = os.path.join(media_root,filename)
                                        try:
                                            shutil.copy(image_path, new_filepath)
                                        except (IOError, OSError) as e:
                                            print(f"Error copying file: {e}")
                                    if difficulty.topic.topic_name == "Homographs":
                                        if "HG"+request.POST['wordToEdit'] == os.path.splitext(filename)[0][:-1]:
                                            new_filename = filename.replace("HG"+request.POST["wordToEdit1"], "HG"+request.POST["inputField2"])
                                            new_filepath = os.path.join(media_root, new_filename)
                                            image_path = os.path.join(media_root,filename)
                                            try:
                                                shutil.copy(image_path, new_filepath)
                                            except (IOError, OSError) as e:
                                                print(f"Error copying file: {e}")
                                break
                pictureIsDelete = False
                difficulty_check_all = Difficulty.objects.all()
                for difficulty_check in difficulty_check_all:
                    if difficulty_check.topic.topic_name == "Synonyms":
                        words = difficulty_check.words.split(",")
                        if request.POST['wordToEdit1'] in words:
                            pictureIsDelete = True
                            break
                    else:
                        words = difficulty_check.words.split(",")
                        words1 = difficulty_check.words1.split(",")
                        if request.POST['wordToEdit1'] in words or request.POST['wordToEdit1'] in words1:
                            pictureIsDelete = True
                            break
                if pictureIsDelete == False:
                    for filename in os.listdir(media_root):
                        if request.POST['wordToEdit1'] == os.path.splitext(filename)[0][:-1]:
                            file_path = os.path.join(settings.MEDIA_ROOT,filename)
                            os.remove(file_path)
                        if difficulty.topic.topic_name == "Homographs":
                                if "HG"+request.POST['wordToEdit1'] == os.path.splitext(filename)[0][:-1]:
                                    file_path = os.path.join(settings.MEDIA_ROOT,filename)
                                    os.remove(file_path)
            return render(request,'teacherDashboard.html')

        elif request.POST.get("wordToDelete"):

            wordToDelete = False
            difficulty = Difficulty.objects.get(difficulty_id=request.POST['topicIdWord1Delete'])

            wordArray = difficulty.words.split(",")
            wordArray1 = difficulty.words1.split(",")
            index = wordArray.index(request.POST["wordToDelete"])
            wordArray.remove(request.POST["wordToDelete"])
            wordArray1.pop(index)
            difficulty.words = ",".join(wordArray)
            difficulty.words1 = ",".join(wordArray1)
            difficulty.save()
            difficulty_check_all = Difficulty.objects.all()
            for difficulty_check in difficulty_check_all:
                if difficulty_check.topic.topic_name == "Synonyms":
                    words = difficulty_check.words.split(",")
                    if request.POST["wordToDelete"] in words:
                        wordToDelete = True
                        break
                else:
                    words = difficulty_check.words.split(",")
                    words1 = difficulty_check.words1.split(",")
                    if request.POST["wordToDelete"] in words or request.POST["wordToDelete"] in words1:
                        wordToDelete = True
                        break
            if wordToDelete == False:
                for filename in os.listdir(media_root):
                    if request.POST['wordToDelete'] == os.path.splitext(filename)[0][:-1] or "HG"+request.POST['wordToDelete'] == os.path.splitext(filename)[0][:-1]:
                        image_path = os.path.join(media_root,filename)
                        os.remove(image_path)
            return render(request,'teacherDashboard.html')

        elif request.POST.get("wordToDelete1"):

            wordToDelete = False
            difficulty = Difficulty.objects.get(difficulty_id=request.POST['topicIdWord2Delete'])

            wordArray = difficulty.words.split(",")
            wordArray1 = difficulty.words1.split(",")
            index = wordArray1.index(request.POST["wordToDelete1"])
            wordArray1.remove(request.POST["wordToDelete1"])
            wordArray.pop(index)
            difficulty.words = ",".join(wordArray)
            difficulty.words1 = ",".join(wordArray1)
            difficulty.save()
            difficulty_check_all = Difficulty.objects.all()
            for difficulty_check in difficulty_check_all:
                if difficulty_check.topic.topic_name == "Synonyms":
                    words = difficulty_check.words.split(",")
                    if request.POST["wordToDelete1"] in words:
                        wordToDelete = True
                        break
                else:
                    words = difficulty_check.words.split(",")
                    words1 = difficulty_check.words1.split(",")
                    if request.POST["wordToDelete1"] in words or request.POST["wordToDelete1"] in words1:
                        wordToDelete = True
                        break
            if wordToDelete == False:
                for filename in os.listdir(media_root):
                    if request.POST['wordToDelete1'] == os.path.splitext(filename)[0][:-1] or "HG"+request.POST['wordToDelete1'] == os.path.splitext(filename)[0][:-1]:
                        image_path = os.path.join(media_root,filename)
                        os.remove(image_path)
            return render(request,'teacherDashboard.html')


class StudentDashboard(TemplateView):
    template_name = 'studentDashboard.html'
    login_url = '/studentlogin/'
    def get(self,request):
        try:
            user = AdminUser.objects.get(username=request.session['username'])
            topics = Topics.objects.filter(owner_id=user.admin_id)
            topic_list = []
            for topic in topics:
                easyQuery = Difficulty.objects.get(topic_id = topic.topic_id, difficulty_name='easy')
                easyWordCount = easyQuery.words.split(',')
                mediumQuery = Difficulty.objects.get(topic_id = topic.topic_id, difficulty_name='medium')
                mediumWordCount = mediumQuery.words.split(',')
                difficultQuery = Difficulty.objects.get(topic_id = topic.topic_id, difficulty_name='difficult')
                difficultWordCount = difficultQuery.words.split(',')
                topic_dict = {
                    'topic_name': topic.topic_name,
                    'topic_id': topic.topic_id,
                    'question_answered_easy': easyQuery.answered,
                    'question_answered_medium':  mediumQuery.answered,
                    'question_answered_difficult': difficultQuery.answered,
                    'easy_word_count': len(easyWordCount),
                    'medium_word_count': len(mediumWordCount),
                    'difficult_word_count': len(difficultWordCount),
                    # Add more attributes as needed
                }
                topic_list.append(topic_dict)
            return render(request,'studentDashboard.html',{'topics':topic_list,'user':user})
        except:

            return redirect('/studentlogin/')

    def post(self,request):
        if request.POST.get('difficulty') == 'easy':
            try:
                questions = Difficulty.objects.get(difficulty_name='easy',topic_id=request.POST.get('topic_id'))
                return JsonResponse({'questions': questions.difficulty_id})
            except:
                return redirect('/studentdashboard/')
        elif request.POST.get('difficulty') == 'medium':
            try:
                questions = Difficulty.objects.get(difficulty_name='medium',topic_id=request.POST.get('topic_id'))
                return JsonResponse({'questions': questions.difficulty_id})
            except:
                return redirect('/studentdashboard/')
        elif request.POST.get('difficulty') == 'difficult':
            try:
                questions = Difficulty.objects.get(difficulty_name='difficult',topic_id=request.POST.get('topic_id'))
                return JsonResponse({'questions': questions.difficulty_id})
            except:
                return redirect('/studentdashboard/')
        elif request.POST.get('resetdifficulty') == 'easy':
            try:
                questions = Difficulty.objects.get(difficulty_name='easy',topic_id=request.POST.get('topic_id_reset'))
                questions.answered = 0
                questions.score = 0
                questions.save()
                return JsonResponse({'isReset': True})
            except:
                return redirect('/studentdashboard/')
        elif request.POST.get('resetdifficulty') == 'medium':
            try:
                questions = Difficulty.objects.get(difficulty_name='medium',topic_id=request.POST.get('topic_id_reset'))
                questions.answered = 0
                questions.score = 0
                questions.save()
                return JsonResponse({'isReset': True})
            except:
                return redirect('/studentdashboard/')
        elif request.POST.get('resetdifficulty') == 'difficult':
            try:
                questions = Difficulty.objects.get(difficulty_name='difficult',topic_id=request.POST.get('topic_id_reset'))
                questions.answered = 0
                questions.score = 0
                questions.save()
                return JsonResponse({'isReset': True})
            except:
                return redirect('/studentdashboard/')

class StudentActivity(TemplateView):

    def get(self,request):
        def generate_two_random_numbers():
            number1 = random.randint(0,4)  # Generate a random integer between 0 and 4 (inclusive)
            number2 = random.randint(0,4)  # Generate another random integer between 0 and 4 (inclusive)

            # Ensure that number2 is different from number1
            while number2 == number1:
                number2 = random.randint(1,5)
            return number1,number2
        def fetch_words(difficulty):
            if difficulty == 'easy':
                num = random.randint(3, 4)
            elif difficulty == 'medium':
                num = random.randint(4, 5)
            elif difficulty == 'difficult':
                num = random.randint(5, 6)

            url = f"https://random-word-api.herokuapp.com/word?length={num}"
            response = requests.get(url)

            if response.status_code == 200:
                words = response.json()
                return words[0]
            else:
                print('Error fetching word')

        def fetch_image(query):
            image_urls = []
            for filename in os.listdir(media_root):
                if query == os.path.splitext(filename)[0][:-1]:
                    image_url = os.path.join(media_url,filename)
                    image_urls.append(image_url)
            return image_urls


        csrf_token = request.META.get('HTTP_COOKIE','').split(';')
        for csrf_value in csrf_token:
            try:
                questions = Difficulty.objects.get(difficulty_id=csrf_value.replace(' ',''))
                break
            except:
                continue

        topic_name = Topics.objects.get(topic_id=questions.topic_id)
        words = questions.words.split(',')
        cleaned_words = [word.strip() for word in words]
        words1 = questions.words1.split(',')
        cleaned_words1 = [word.strip() for word in words1]

        if len(words) < questions.answered:
            questions.answered = len(words)
            questions.maxpoints = questions.maxpoints - questions.points_per_question
            questions.save()

        if questions.score > questions.maxpoints:
            questions.score = questions.maxpoints
            questions.save()

        def checkTopic():
            result = generate_two_random_numbers()
            if topic_name.topic_name == "Synonyms":
                image_url = fetch_image(cleaned_words[persistent_variable-1])
                try:
                    return image_url[result[0]],image_url[result[1]]
                except:
                    image_url = fetch_image(cleaned_words[persistent_variable-1])
                    return image_url[result[0]],image_url[result[1]]
            elif topic_name.topic_name == "Antonyms":
                image_url = fetch_image(cleaned_words1[persistent_variable-1])
                image_url1 = fetch_image(cleaned_words[persistent_variable-1])
                return image_url[result[0]],image_url1[result[1]]
            elif topic_name.topic_name == "Homonyms":
                image_url = fetch_image(cleaned_words[persistent_variable-1])
                image_url1 = fetch_image(cleaned_words1[persistent_variable-1])
                return image_url[result[0]],image_url1[result[1]]
            elif topic_name.topic_name == "Homographs":
                image_url = fetch_image(cleaned_words[persistent_variable-1])
                image_url1 = fetch_image("HG"+cleaned_words1[persistent_variable-1])
                return image_url[result[0]],image_url1[result[1]]
            elif topic_name.topic_name == "Hyponyms":
                image_url = fetch_image(cleaned_words[persistent_variable-1])
                image_url1 = fetch_image(cleaned_words[persistent_variable-1])
                return image_url[result[0]],image_url1[result[1]]

        persistent_variable = cache.get('my_persistent_variable')

        # If the persistent variable doesn't exist yet,initialize it
        if persistent_variable is None:
            persistent_variable = 0
            cache.set('my_persistent_variable',persistent_variable)
        if len(words) == questions.answered:
            img_urls = checkTopic()
            choices = []
            choices1 = []
            try:
                get_choices = Choices.objects.get(difficulty_id=questions.difficulty_id, choices_name=cleaned_words[persistent_variable-1])
                choices1_split = get_choices.word_choices.split(',')
                for word in choices1_split:
                    if word == "":
                        choices.append(fetch_words(questions.difficulty_name))
                    else:
                        choices.append(word)
            except:
                for i in range(3):
                    choices.append(fetch_words(questions.difficulty_name))
            try:
                get_choices1 = Choices.objects.get(difficulty_id=questions.difficulty_id, choices_name=cleaned_words1[persistent_variable-1])
                choices2_split = get_choices1.word_choices.split(',')
                for word in choices2_split:
                    if word == "":
                        choices1.append(fetch_words(questions.difficulty_name))
                    else:
                        choices1.append(word)
            except:
                for i in range(3):
                    choices1.append(fetch_words(questions.difficulty_name))
            choices.append(cleaned_words[questions.answered-1])
            choices1.append(cleaned_words1[questions.answered-1])
            random.shuffle(choices)
            random.shuffle(choices1)

            return render(request,'studentActivity.html',{'questions':questions,'words': cleaned_words[questions.answered-1],'words1': cleaned_words1[questions.answered-1],'start_index':questions.answered,
                                                         'img_url':img_urls[0],'img_url2': img_urls[1],'length':len(words),'choices':choices,'choices1':choices1,'answered':'done'})
        # Increment the persistent variable
        persistent_variable = questions.answered + 1
        cache.set('my_persistent_variable',persistent_variable)
        img_urls = checkTopic()
        choices = []
        choices1 = []
        try:
            get_choices = Choices.objects.get(difficulty_id=questions.difficulty_id, choices_name=cleaned_words[persistent_variable-1])
            choices1_split = get_choices.word_choices.split(',')
            for word in choices1_split:
                if word == "":
                    choices.append(fetch_words(questions.difficulty_name))
                else:
                    choices.append(word)
        except:
            for i in range(3):
                choices.append(fetch_words(questions.difficulty_name))
        try:
            get_choices1 = Choices.objects.get(difficulty_id=questions.difficulty_id, choices_name=cleaned_words1[persistent_variable-1])
            choices2_split = get_choices1.word_choices.split(',')
            for word in choices2_split:
                if word == "":
                    choices1.append(fetch_words(questions.difficulty_name))
                else:
                    choices1.append(word)
        except:
            for i in range(3):
                choices1.append(fetch_words(questions.difficulty_name))

        choices.append(cleaned_words[persistent_variable-1])
        choices1.append(cleaned_words1[persistent_variable-1])
        random.shuffle(choices)
        random.shuffle(choices1)
        return render(request,'studentActivity.html',{'questions':questions,'words': cleaned_words[persistent_variable-1],'words1': cleaned_words1[persistent_variable-1],'start_index':persistent_variable,
                                                         'img_url':img_urls[0],'img_url2': img_urls[1],'length':len(words),'choices':choices,'choices1':choices1})
    def post(self,request):
        if request.POST.get('choice'):
            persistent_variable = cache.get('my_persistent_variable')
            csrf_token = request.META.get('HTTP_COOKIE','').split(';')
            for csrf_value in csrf_token:
                try:
                    questions = Difficulty.objects.get(difficulty_id=csrf_value.replace(' ',''))
                    break
                except:
                    continue
            words = questions.words.split(',')

            cleaned_words = [word.strip() for word in words]

            if request.POST.get('choice') != cleaned_words[persistent_variable-1]:
                return JsonResponse({'answerVerify': False,'correct_answer':cleaned_words[persistent_variable-1]})
            else:
                return JsonResponse({'answerVerify': True,'points_per_question':questions.points_per_question})
        elif request.POST.get('choice1'):
            persistent_variable = cache.get('my_persistent_variable')
            csrf_token = request.META.get('HTTP_COOKIE','').split(';')
            for csrf_value in csrf_token:
                try:
                    questions = Difficulty.objects.get(difficulty_id=csrf_value.replace(' ',''))
                    break
                except:
                    continue

            words1 = questions.words1.split(',')

            cleaned_words1 = [word.strip() for word in words1]

            if request.POST.get('choice1') != cleaned_words1[persistent_variable-1]:
                return JsonResponse({'answerVerify': False,'correct_answer':cleaned_words1[persistent_variable-1]})
            else:
                return JsonResponse({'answerVerify': True,'points_per_question':questions.points_per_question})
        else:
            if request.POST.get('isCorrect') == "correct":
                csrf_token = request.META.get('HTTP_COOKIE','').split(';')
                for csrf_value in csrf_token:
                    try:
                        questions = Difficulty.objects.get(difficulty_id=csrf_value.replace(' ',''))
                        break
                    except:
                        continue
                questions.score = questions.score + questions.points_per_question
                questions.answered = questions.answered + 1
                questions.save()
            else:
                csrf_token = request.META.get('HTTP_COOKIE','').split(';')
                for csrf_value in csrf_token:
                    try:
                        questions = Difficulty.objects.get(difficulty_id=csrf_value.replace(' ',''))
                        break
                    except:
                        continue
                questions.answered = questions.answered + 1
                questions.save()

class StudentLogin(TemplateView):
    template_name = 'studentLogin.html'

    def post(self,request):
        if request.POST.get('admin_key'):
            try:
                admin_user = AdminUser.objects.get(user_key=request.POST['admin_key'])
                username = admin_user.username
                password = admin_user.password
                user = authenticate(request,username=username,password=password)
                if user is not None:
                    login(request,user)
                    request.session['username'] = username
                    request.session.save()
                    print("if ok")
                    return JsonResponse({'adminKeyVerify': True})
            except:
                print("ok")
                return JsonResponse({'adminKeyVerify': False})


class TopicPage(TemplateView):
    template_name = 'topicPage.html'