from database import (
    get_user_reservations,
    delete_reservation,
)


def cancel_user_reservation(user_id):
    reservations = get_user_reservations(user_id)

    if not reservations:
        return False

    reservation_id = reservations[0][0]

    delete_reservation(reservation_id)

    return True
