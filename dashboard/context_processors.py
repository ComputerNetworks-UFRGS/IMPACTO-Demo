
def user_type(request):
    if request.user.is_authenticated:
        return {
            'is_instructor': request.user.is_instructor,
            'is_student': request.user.is_student,
        }
    return {
        'is_instructor': False,
        'is_student': False,
    }