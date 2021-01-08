from django.db import models
from django.db.models import F 
from django.db.models import Min
from django.db.models import Max


class Board(models.Model):
    session_id = models.CharField(max_length=40, null=False)
    game_id = models.CharField(max_length=20, null=False)
    modified = models.DateTimeField(auto_now_add=True)

class Allowed_Moves(models.Model):
    xn = models.IntegerField(null=False)
    yn = models.IntegerField(null=False)
    game = models.ForeignKey(Board)
    
class Token(models.Model):
    token_type = models.IntegerField(null=False) 
    player = models.BooleanField(null=False)
    xn = models.IntegerField(null=False)
    yn = models.IntegerField(null=False)
    choosen = models.BooleanField(blank=True, default=False)
    game = models.ForeignKey(Board)   
    class Meta:
        unique_together = ("xn", "yn", "game")
        
    def is_occupied(self):
        occupied = Token.objects.filter(game=self.game_id, xn=self.xn, yn=self.yn)
        amount = occupied.count()
        if amount > 0:
            return True
        else:
            return False
        
    def is_circle(self):
        tok_type = Token.objects.filter(game=self.game_id, xn=self.xn, yn=self.yn).values('token_type')
        if tok_type.count() > 0:
            if int(tok_type[0]['token_type']) == 1:
                return True
            else:
                return False
        else:
            return False
        
    def is_choosen(self):
        choosen_amount = Token.objects.filter(game=self.game_id, choosen=True).count()
        if choosen_amount > 0:
            return True
        else:
            return False

    def count_moves(self):
        moves = Token.objects.filter(game=self.game_id).count()
        return moves
    
    def get_previous_click(self):
        previous_click = Token.objects.filter(game=self.game_id, token_type=1, choosen=True).values('xn','yn')
        if previous_click.count():
            previous_xn = previous_click[0]['xn']
            previous_yn = previous_click[0]['yn']
            previous = {'xn': previous_xn, 'yn': previous_yn}
        else:
            previous = None
        return previous
        
    def calc_allowed_moves(self, limits, ext_lim):
        for key in limits:
            x_lim = int(limits[key]['xn'])
            y_lim = int(limits[key]['yn'])
            sorted_x = sorted([self.xn, x_lim]) 
            sorted_y = sorted([self.yn, y_lim])
            if key.startswith('vert'):
                for yi in range(sorted_y[0], sorted_y[1]):
                    ini = {'xn': x_lim, 'yn': yi, 'game_id': self.game_id}
                    move = Allowed_Moves(**ini)
                    move.save()
            if key.startswith('horiz'):
                for xi in range(sorted_x[0], sorted_x[1]):
                    ini = {'xn': xi, 'yn': y_lim, 'game_id': self.game_id}
                    move = Allowed_Moves(**ini)
                    move.save()
            if key.startswith('diag'):
                for xi in range(sorted_x[0], sorted_x[1]):
                    yi = self.yn + (xi - self.xn)*(y_lim - self.yn)/(x_lim - self.xn)
                    ini = {'xn': xi, 'yn': yi, 'game_id': self.game_id}
                    move = Allowed_Moves(**ini)
                    move.save()
        if ext_lim is not None:
            for key in ext_lim:
                if ext_lim[key] is not None:
                    x_lim = int(ext_lim[key]['xn'])
                    y_lim = int(ext_lim[key]['yn'])
                    ini = {'xn': x_lim, 'yn': y_lim, 'game_id': self.game_id}
                    move = Allowed_Moves(**ini)
                    move.save()

    def delete_touch(self, x, y):
        player_click = Token.objects.filter(game=self.game_id, token_type=1, player=1, xn=x, yn=y)
        if player_click.count():
            player_click.delete()

    def change_disk_color(self, previous):
        board = Token.objects.filter(game=self.game_id)
        disks = board.filter(token_type=2)
        x1 = int(previous['xn'])
        y1 = int(previous['yn'])
        x2 = self.xn
        y2 = self.yn
        sorted_x = sorted([x1,x2])
        sorted_y = sorted([y1,y2])
        if disks.count() > 0:
            if x1 == x2 and y1 == y2:
                change = None
            else:
                if x1 == x2:
                    change = disks.filter(xn=x1, yn__gt=sorted_y[0], yn__lt=sorted_y[1])
                if y1 == y2:
                    change = disks.filter(yn=y1, xn__gt=sorted_x[0], xn__lt=sorted_x[1])
                if x1 != x2 and y1 != y2:
                    change = disks.filter(xn__gt=sorted_x[0], xn__lt=sorted_x[1], yn__gt=sorted_y[0], yn__lt=sorted_y[1], yn=y1+(F('xn')-x1)*(y2-y1)/(x2-x1))
            if change.count() > 0:
                #change.update(player = bool(~bool(F('player'))))
                #change.update(player = not F('player'))
                change.update(player = 1-F('player'))
                change_list = list(change.values('xn','yn','player'))
                return change_list
            else:
                return None
        else:
            return None

    def get_limits(self):
        board = Token.objects.filter(game=self.game_id)
        vertical = board.filter(xn = self.xn)
        horizontal = board.filter(yn = self.yn)
        main_diagonal = board.filter(yn = self.yn + self.xn - F('xn'))
        diagonal = board.filter(yn = self.yn - self.xn + F('xn'))
        vertical_gt = vertical.filter(yn__gt = self.yn)
        vertical_lt = vertical.filter(yn__lt = self.yn)
        horizontal_gt = horizontal.filter(xn__gt = self.xn)
        horizontal_lt = horizontal.filter(xn__lt = self.xn)
        diagonal_gt = diagonal.filter(xn__gt = self.xn, yn__gt = self.yn)
        diagonal_lt = diagonal.filter(xn__lt = self.xn, yn__lt = self.yn)

        limits = {}
        ext_lim = {}
        amount = 0
        valid = True
   #     limit_queries = {'vert_gt': vertical_gt, 'vert_lt': vertical_lt, 'horiz_gt': horizontal_gt, 'horiz_lt': horizontal_lt, 'diag_gt': diagonal_gt, 'diag_lt': diagonal_lt}
        limit_queries = {'vert_gt': vertical_gt, 'vert_lt': vertical_lt, 'horiz_gt': horizontal_gt, 'horiz_lt': horizontal_lt}
        diag_queries = {'diag_gt': diagonal_gt, 'diag_lt': diagonal_lt}

        if self.xn == 0:
            y_min = -5
            y_max = 5
        if self.xn == -5:
            y_min = -5
            y_max = 0
        if self.xn == 5:
            y_min = 0
            y_max = 5
        if self.xn in [1,2,3,4]:
            y_min = self.xn - 5 -1
            y_max = 5 +1
        if self.xn in [-4,-3,-2,-1]:
            y_min = -5 - 1
            y_max = self.xn + 5 + 1
                
        if self.yn == 0:
            x_min = -5
            x_max = 5
        if self.yn == -5:
            x_min = -5
            x_max = 0
        if self.yn == 5:
            x_min = 0
            x_max = 5
        if self.yn in [1,2,3,4]:
            x_min = self.yn - 5 -1
            x_max = 5 + 1
        if self.yn in [-4,-3,-2,-1]:
            x_min = -5 - 1
            x_max = self.yn + 5 +1
 
        for key in limit_queries:
            query_n = limit_queries[key].annotate(norma=(F('xn')-self.xn)*(F('xn')-self.xn)+(F('yn')-self.yn)*(F('yn')-self.yn))
            query_m = query_n.aggregate(min_norma=Min((F('xn')-self.xn)*(F('xn')-self.xn)+(F('yn')-self.yn)*(F('yn')-self.yn)))['min_norma']
            sign_x = 1
            sign_y = 1
            if query_m is not None:
                limits[key] = query_n.filter(norma=int(query_m)).values('xn','yn','token_type')[0]
                x_lim = int(limits[key]['xn'])
                y_lim = int(limits[key]['yn'])
                x = x_lim
                y = y_lim
                if self.xn >= x_lim:
                    sign_x = 1
                else:
                    sign_x = -1
                if self.yn >= y_lim:
                    sign_y = 1
                else:
                    sign_y = -1                    
                if int(limits[key]['token_type']) == 2:
                    if key.startswith('vert'):
                        y = y - sign_y
                        amount = board.filter(xn=self.xn, yn=y, token_type=2).count()
                        while amount != 0:
                            y = y - sign_y
                            amount = board.filter(xn=self.xn, yn=y, token_type=2).count()
                        ext_lim[key] = {"xn": self.xn, "yn": y}
                    if key.startswith('horiz'):
                        x = x - sign_x
                        amount = board.filter(xn=x, yn=self.yn, token_type=2).count()
                        while amount != 0:
                            x = x - sign_x
                            amount = board.filter(xn=x, yn=self.yn, token_type=2).count()
                        ext_lim[key] = {"xn": x, "yn": self.yn}
            else:               
                if key == 'vert_gt':
                    limits[key] = {"xn": self.xn, "yn": y_max}
                if key == 'vert_lt':
                    limits[key] = {"xn": self.xn, "yn": y_min}
                if key == 'horiz_gt':
                    limits[key] = {"xn": x_max, "yn": self.yn}
                if key == 'horiz_lt':
                    limits[key] = {"xn": x_min, "yn": self.yn}

        if self.xn < self.yn:
            x_min = -5 - 1
            y_min = x_min + self.yn - self.xn
            if self.yn - self.xn == 5:
                y_max = 4 + 1
            else:
                y_max = 5 + 1
            x_max = y_max - self.yn + self.xn
        else:
            if self.xn == self.yn:
                y_min = -4 - 1
                x_max = 4 + 1
            else:
                y_min = -5 - 1
                x_max = 5 + 1
            x_min = y_min - self.yn + self.xn
            y_max = x_max + self.yn - self.xn
                
        if self.xn == self.yn - 5:
            x_min = -4 - 1
            y_min = x_min + self.yn - self.xn

        if self.yn - self.xn == -5:
            x_max = 4 + 1
            y_max = x_max + self.yn - self.xn
            y_min = -4 - 1
            x_min = y_min - self.yn + self.xn
 
        for key in diag_queries:
            query_n = diag_queries[key].annotate(norma=(F('xn')-self.xn)*(F('xn')-self.xn)+(F('yn')-self.yn)*(F('yn')-self.yn))
            query_m = query_n.aggregate(min_norma=Min((F('xn')-self.xn)*(F('xn')-self.xn)+(F('yn')-self.yn)*(F('yn')-self.yn)))['min_norma']
            if query_m is not None:
                limits[key] = query_n.filter(norma=int(query_m)).values('xn','yn','token_type')[0]
                x_lim = int(limits[key]['xn'])
                y_lim = int(limits[key]['yn'])
                x = x_lim
                y = y_lim
                if self.xn >= x_lim:
                    sign_x = 1
                else:
                    sign_x = -1
                if self.yn >= y_lim:
                    sign_y = 1
                else:
                    sign_y = -1 
                    x = x - sign_x
                if int(limits[key]['token_type']) == 2:    
                    if x_lim != self.xn:
                        y = self.yn + (x - self.xn)*(y_lim - self.yn)/(x_lim - self.xn)
                        amount = board.filter(xn=x, yn=y, token_type=2).count()
                        while amount != 0 and x_lim != self.xn:
                            x = x - sign_x
                            y = self.yn + (x - self.xn)*(y_lim - self.yn)/(x_lim - self.xn)
                            amount = board.filter(xn=x, yn=y, token_type=2).count()
                        ext_lim[key] = {"xn": x, "yn": y}
            else:               
                if key == 'diag_gt':
                    limits[key] = {"xn": x_max, "yn": y_max}
                if key == 'diag_lt':    
                    limits[key] = {"xn": x_min, "yn": y_min}

        for key in ext_lim:
            #valid = True
            if ext_lim[key] is not None:
                x = int(ext_lim[key]['xn'])
                y = int(ext_lim[key]['yn'])
                if board.filter(xn=x, yn=y).count() > 0:
                    valid = False
                if (abs(x) > 5) or (abs(y) > 5) or (x*y == 25):
                    valid = False
                if (abs(x) == 5) and (y == 0):
                    valid = False
                if (abs(y) == 5) and (x == 0):
                    valid = False
                if (abs(x) + abs(y) >= 6) and (x*y < 0) and (abs(x) >= 3) and (abs(y) <= 3):
                    valid = False
                if (abs(x) + abs(y) >= 6) and (x*y < 0) and (abs(x) <= 3) and (abs(y) >= 3):
                    valid = False
                if not valid:
                    ext_lim[key] = None
                    valid = True
      
        return limits, ext_lim
