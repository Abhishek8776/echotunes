from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
  print('one')
  def save_user(self, request, sociallogin, form=None):
    print('two')
    user = super().save_user(request, sociallogin, form=form)
    if sociallogin.account.provider == 'google':
        extra_data = sociallogin.account.extra_data
        if 'name' in extra_data:
            user.name = extra_data['name']
        if 'email' in extra_data:
            user.email = extra_data['email']
        user.save()
    return user
  
# @receiver(user_signed_up)
# def retrieve_social_data(request, user, **kwargs):
#     """Signal, that gets extra data from sociallogin and put it to profile."""
#     # get the profile where i want to store the extra_data
#     profile = Account(user=user)
#     # in this signal I can retrieve the obj from SocialAccount
#     data = SocialAccount.objects.filter(user=user, provider='google')
#     # check if the user has signed up via social media
#     if data:
#         picture = data[0].get_avatar_url()





