from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
import datetime
import json
from game.models import *

def index(request):
    response = TemplateResponse(request, 'play.html', {})
    sessionid = request.session.session_key
    if not request.session.exists(sessionid):
        request.session.create()
    return response

def play(request):
    if request.is_ajax():
        sessionid = request.session.session_key
        if request.session.exists(sessionid) and 'game_id' in request.GET:
            response = TemplateResponse(request, 'play.html', {})
            gameid = request.GET['game_id']
            initial = {'session_id': sessionid, 'game_id': gameid}
            newboard = Board(**initial)
            newboard.save()
            return response
        else:
            return redirect('/')
    else:
        return redirect('/')

def close(request):
    if request.is_ajax():
        sessionid = request.session.session_key
        if request.session.exists(sessionid) and 'game_id' in request.GET:
            gameid = request.GET['game_id']
            #game = Board.objects.get(session_id=sessionid, game_id=gameid)
            game = Board.objects.get(game_id=gameid)
            Token.objects.filter(game_id=game.pk).delete()
            game.delete()
            expired = datetime.datetime.now() - datetime.timedelta(hours=48)
            oldgame = Board.objects.filter(modified__lt=expired)
            oldgame.delete()
            request.session.flush()
            request.session.clear()
            response = TemplateResponse(request, 'play.html', {})
        if 'game_id' not in request.GET:
            return redirect('/')
        if not request.session.exists(request.session.session_key):
            request.session.create() 
        return response
    else:
        return redirect('/')

def ajax(request):
    if request.is_ajax() or True:
        previous = None
        if 'game_id' in request.GET and 'x' in request.GET and 'y' in request.GET:
            xx = int(request.GET['x'])
            yy = int(request.GET['y'])
            counter = request.GET['counts']
            gameid = request.GET['game_id']
            sessionid = request.session.session_key

            try:
                game = Board.objects.get(session_id=gameid)

            except Board.DoesNotExist:
                game = Board(sessionid, gameid)
                game.save()

           # game = Board.objects.get(game_id=gameid)
            #game = Board.objects.get(session_id=sessionid, game_id=gameid)
            initial = {'token_type': 1, 'player': True, 'xn': xx, 'yn': yy, 'choosen': False, 'game_id': game.pk}
            touch = Token(**initial)
            moves = touch.count_moves()
            if moves < 5:
                start = True
            else:
                start = False
            occupied = touch.is_occupied()
            tok_type = touch.is_circle()
            allowed = Allowed_Moves.objects.filter(game_id=game.pk)
            check_allowed = False
            if allowed.count():
                if allowed.filter(xn = xx, yn = yy).count():
                    check_allowed = True
                else:
                    check_allowed = False
            else:
                check_allowed = True
            
            choosen = touch.is_choosen()
            if start:
                if not occupied:
                    touch.save()
                    response = JsonResponse({'free': True, 'limits': None, 'previous': previous, 'choosen': choosen, 'occupied': occupied, 'allowed': check_allowed})
                else:
                    response = JsonResponse({'free': False, 'alert_text': 'This position is occupied', 'previous': previous})

            if moves >= 5:
                if not choosen:
                    if occupied and tok_type:
                        #touch.update(choosen=True)
                        Token.objects.filter(game_id=game.pk, xn=xx, yn=yy).update(choosen=True)
                        #touch.save()
                        limits, ext_lim = touch.get_limits()
                        game.save()
                        move = Allowed_Moves.objects.filter(game_id=game.pk)
                        move.delete()
                        touch.calc_allowed_moves(limits, ext_lim)
                        response = JsonResponse({'free': True, 'limits': json.dumps(limits), 'ext_lim': json.dumps(ext_lim), 'previous': previous, 'choosen': choosen, 'occupied': occupied, 'allowed': check_allowed})
                    else:
                        response = JsonResponse({'free': False, 'alert_text': 'You must choose one of your circles', 'previous': previous})
                else:
                    previous = touch.get_previous_click()
                    old_x = int(previous['xn'])
                    old_y = int(previous['yn'])

                    if check_allowed and not occupied and (old_x != xx or old_y != yy):
                        touch.save()
                        #if previous != None and moves > 5:
                        #if moves > 5:
                           # touch.delete_touch(int(previous['xn']), int(previous['yn']))
                        Token.objects.filter(game_id=game.pk, choosen=True).delete()
                        move = Allowed_Moves.objects.filter(game_id=game.pk)
                        move.delete()
                        initial = {'token_type': 2, 'player': True, 'xn': old_x, 'yn': old_y, 'choosen': False, 'game_id': game.pk}
                        disk = Token(**initial)
                        disk.save()
                        changed = touch.change_disk_color(previous)
                        response = JsonResponse({'free': True, 'limits': None, 'previous': previous, 'changed': json.dumps(changed), 'choosen': choosen, 'occupied': occupied, 'allowed': check_allowed})
                        #else:
                            #response = JsonResponse({'free': False, 'alert_text': 'This move is not allowed1', 'previous': previous, 'choosen': choosen, 'occupied': occupied, 'allowed': check_allowed})
                    else:
                        response = JsonResponse({'free': False, 'alert_text': 'This move is not allowed', 'previous': previous, 'choosen': choosen, 'occupied': occupied, 'allowed': check_allowed})

                    if old_x == xx and old_y == yy and occupied:
                        Token.objects.filter(game_id=game.pk, xn=xx, yn=yy).update(choosen=False)
                        move = Allowed_Moves.objects.filter(game_id=game.pk)
                        move.delete()
                        response = JsonResponse({'free': True, 'limits': None, 'previous': previous})
            return response
        else:
            return redirect('/')
    else:
        return redirect('/')
