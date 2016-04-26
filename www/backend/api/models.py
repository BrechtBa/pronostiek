from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.models import Group as AuthGroup
from django.db.models.signals import post_save
from rest_framework_jwt.utils import jwt_payload_handler as base_jwt_payload_handler

from .utils import unixtimestamp

# model definition
################################################################################
# Users
################################################################################
class UserProfile(models.Model):
	user = models.OneToOneField(AuthUser, on_delete=models.SET_NULL, related_name='profile', blank=True, null=True)
	avatar = models.CharField(max_length=512, blank=True, default='')

	
class Points(models.Model):
	user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='points', blank=True, null=True)
	prono = models.CharField(max_length=100, blank=True, default='')
	points = models.IntegerField(blank=True, default=0)
	
	def __str__(self):
		return '{}'.format(self.points)	
	
################################################################################
# Competition
################################################################################

class Group(models.Model):
	name = models.CharField(max_length=100, blank=True, default='')
	
	def save(self, *args, **kwargs):
		super(Group, self).save(*args, **kwargs)
		
		# create prono results for all users
		for user in AuthUser.objects.all(): 
			check_user(user)

	def __str__(self):
		return '{}'.format(self.name)	
		

class Team(models.Model):
	name = models.CharField(max_length=100, blank=True, default='')
	abr = models.CharField(max_length=5, blank=True, default='')
	icon = models.CharField(max_length=256, blank=True, default='')
	iso_icon = models.CharField(max_length=5, blank=True, default='')
	group = models.ForeignKey(Group,on_delete=models.SET_NULL,related_name='teams', blank=True, null=True)
	groupstage_points = models.FloatField(blank=True, default=0)
	
	def __str__(self):
		return '{}'.format(self.name)

		
class Match(models.Model):
	team1 = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='matches_team1', blank=True, null=True)
	team2 = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='matches_team2', blank=True, null=True)
	defaultteam1 = models.CharField(max_length=5, blank=True, default='')
	defaultteam2 = models.CharField(max_length=5, blank=True, default='')
	date = models.BigIntegerField(blank=True, default=0)
	stage = models.IntegerField(blank=True, default=0)
	group = models.ForeignKey(Group, on_delete=models.SET_NULL,related_name='matches', blank=True, null=True)
	position = models.IntegerField(blank=True,default=0)
	
	def save(self, *args, **kwargs):
		super(Match, self).save(*args, **kwargs)
		
		# create a match result
		match_result = MatchResult(match=self)
		match_result.save()

		# create prono results for all users
		for user in AuthUser.objects.all(): 
			check_user(user)
		
	def __str__(self):
		return '{}'.format(self.id)
		
	
class MatchResult(models.Model):
	match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result', blank=True, null=True)
	score1 = models.IntegerField(blank=True, default=-1)
	score2 = models.IntegerField(blank=True, default=-1)
	penalty1 = models.IntegerField(blank=True, default=-1)
	penalty2 = models.IntegerField(blank=True, default=-1)
	
	def save(self, *args, **kwargs):
		super(MatchResult, self).save(*args, **kwargs)
		
		# recalculate the points for all users
		calculate_points()
	
	def __str__(self):
		return '{} - {}'.format(self.score1, self.score2)
	
	

################################################################################
# Prono
################################################################################
class PronoResult(models.Model):
	match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='prono_result', blank=True, null=True)
	user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='prono_result', blank=True, null=True)
	score1 = models.IntegerField(blank=True, default=-1)
	score2 = models.IntegerField(blank=True, default=-1)
	
	def __str__(self):
		return '{} - {}'.format(self.score1, self.score2)


class PronoGroupstageWinners(models.Model):
	user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='prono_groupstage_winners', blank=True, null=True)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='prono_groupstage_winners', blank=True, null=True)
	ranking = models.IntegerField(blank=True, default=-1)
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='prono_groupstage_winners', blank=True, null=True)
	

class PronoKnockoutstageTeams(models.Model):
	user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='prono_knockoutstage_teams', blank=True, null=True)
	stage = models.IntegerField(blank=True, default=-1)
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='prono_knockoutstage_teams', blank=True, null=True)
	
	
class PronoTotalGoals(models.Model):
	user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='prono_total_goals', blank=True, null=True)
	goals = models.IntegerField(blank=True, default=-1)
	
	
class PronoTeamResult(models.Model):
	user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='prono_team_result', blank=True, null=True)
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='prono_team_result', blank=True, null=True)
	result = models.IntegerField(blank=True, default=-1)
	
	


	
# helper elements	
################################################################################
# signals
################################################################################
def prepare_user(sender, **kwargs):
	"""
	performs actions new user is created
	"""
	
	user = kwargs["instance"]
	if kwargs["created"]:
		check_user(user)
	
	if user.is_staff:
		check_matches()

post_save.connect(prepare_user, sender=AuthUser)



def check_matches():
	"""
	checks if all database entries are present for all matches
	"""
	# check if all matches have a result
	for match in Match.objects.all():
		try:
			match.result
		except:
			result = MatchResult(match=match)
			result.save()
			#print('Added result for match {}'.format(match))
		
	
def check_user(user):
	"""
	checks if all database entries are present for the user
	"""
	#print('check {}'.format(user.username))
	############################################################################
	# check if the user has a profile
	try:
		user.profile
	except:
		user_profile = UserProfile(user=user)
		user_profile.save()
		

	############################################################################
	# check if the user has points entries for all pronos	
	for prono in ['total','groupstage_result','groupstage_score','knockoutstage_result','knockoutstage_score','groupstage_winners','knockoutstage_teams','total_goals','team_result']:
		if not prono in [p.prono for p in user.points.all()]:
			user_points = Points(user=user, prono=prono)
			user_points.save()
			#print('Added points for user {} on prono {}'.format(user,prono))
		


	############################################################################
	# check if the user has entries for all pronos
	############################################################################
	# groupstage and knockoutstage result
	for match in Match.objects.all():
		if len(user.prono_result.filter(match=match)) == 0:
			prono = PronoResult(user=user,match=match)
			prono.save()
			#print('Added prono_result for user {} on match {}'.format(user,match))

	############################################################################
	# groupstage_winners
	for ranking in [1,2]:
		for group in Group.objects.all():
			if len(user.prono_groupstage_winners.filter(group=group,ranking=ranking)) == 0:
				prono = PronoGroupstageWinners(user=user,group=group,ranking=ranking)
				prono.save()
				#print('Added prono_groupstage_winners {} for user {} on group {}'.format(ranking,user,group))

	############################################################################
	# knockoutstage_teams
	stages = get_stages()

	# remove the largest stage
	if len(stages) > 0:
		if stages[0] == 0:
			del stages[0]

		# add 1 for the winner
		stages.append(1)

		for stage in stages:
			pronos = user.prono_knockoutstage_teams.filter(stage=stage)
			for i in range(stage-len(pronos)):
				prono = PronoKnockoutstageTeams(user=user,stage=stage)
				prono.save()
				#print('Added prono_knockoutstage_teams {} for user {} on stage {}'.format(i+1,user,stage))

	############################################################################
	# total_goals
	pronos = user.prono_total_goals.all()
	if len(pronos) == 0:
		prono = PronoTotalGoals(user=user)
		prono.save()


	############################################################################
	# team_result
	for team in Team.objects.all():
		pronos = user.prono_team_result.filter(team=team)
		if len(pronos) == 0:
			prono = PronoTeamResult(user=user,team=team)
			prono.save()


def calculate_points():
	for user in AuthUser.objects.all():
		userpoints = calculate_user_points(user)
		
		for points in user.points.all():
			if points.prono in userpoints:
				points.points = userpoints[points.prono]
				points.save()
		
		
			
def calculate_user_points(user):
	userpoints = {}
	
	# groupstage
	groupstage_result = 0
	groupstage_score = 0
	for match in Match.objects.filter(stage=0):
		match_result = match.result
		
		for prono_result in match.prono_result.filter(user=user):
			match_played = match_result.score1 >-1 and match_result.score2 > -1
			team1winscorrect = (prono_result.score1 > prono_result.score2) and (match_result.score1 > match_result.score2)
			team2winscorrect = (prono_result.score1 < prono_result.score2) and (match_result.score1 < match_result.score2)
			tiecorrect = (prono_result.score1 == prono_result.score2) and (match_result.score1 == match_result.score2)
			
			# result correct
			if match_played and (team1winscorrect or team2winscorrect or tiecorrect):
				groupstage_result = groupstage_result + 3
			
			# score correct
			if match_played and (prono_result.score1 == match_result.score1) and ( prono_result.score2 == match_result.score2):
				groupstage_score = groupstage_score + 4
				
	userpoints['groupstage_result'] = groupstage_result
	userpoints['groupstage_score'] = groupstage_score
	
	# knockoutstage
	knockoutstage_result = 0
	knockoutstage_score = 0
	for match in Match.objects.filter(stage__gt=0):
		match_result = match.result
		
		for prono_result in match.prono_result.filter(user=user):
			match_played = match_result.score1 >-1 and match_result.score2 > -1
			team1winscorrect = (prono_result.score1 > prono_result.score2) and (match_result.score1 > match_result.score2)
			team2winscorrect = (prono_result.score1 < prono_result.score2) and (match_result.score1 < match_result.score2)
			tiecorrect = (prono_result.score1 == prono_result.score2) and (match_result.score1 == match_result.score2)
			
			# result correct
			if match_played and (team1winscorrect or team2winscorrect or tiecorrect):
				knockoutstage_result = knockoutstage_result + 6
			
			# score correct
			if match_played and (prono_result.score1 == match_result.score1) and ( prono_result.score2 == match_result.score2):
				knockoutstage_score = knockoutstage_score + 8
				
	userpoints['knockoutstage_result'] = knockoutstage_result
	userpoints['knockoutstage_score'] = knockoutstage_score

	return userpoints
	



def get_stages():
	stages = []
	for match in Match.objects.all():
		if not match.stage in stages:
			stages.append(match.stage)
	stages.sort(reverse=True)
	
	# move the groupstage to the front
	if 0 in stages:
		stages.insert(0, stages.pop(stages.index(0)))

	return stages

################################################################################
# JWT
################################################################################
def jwt_payload_handler(user):
	payload = base_jwt_payload_handler(user)
	
	stages = get_stages()
	
	# get the current stage and the 1st match of the current stage
	currentstage = -1
	firstmatchdate = unixtimestamp() + 24*3600
	for stage in stages:
		# all matches of the stage are in the future
		if len( Match.objects.filter(stage=stage) ) == len(  Match.objects.filter(stage=stage,date__gt=unixtimestamp()+3600) ):
			currentstage = stage
			matches = Match.objects.filter(stage=stage).order_by('date').reverse()
			firstmatchdate = matches[0].date
			break
	
	
	# add aditional data to the payload	
	payload['stage'] = currentstage
	payload['access_exp'] = firstmatchdate-3600
	
	if user.is_staff:
		payload['permission'] = 9
	else:
		payload['permission'] = 1

	return payload
	
	
