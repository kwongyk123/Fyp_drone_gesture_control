from djitellopy import Tello


class GestureController:
    def __init__(self, tello: Tello):
        self.tello = tello
        self._is_landing = False

        # RC control velocities
        self.forw_back_velocity = 0
        self.up_down_velocity = 0
        self.left_right_velocity = 0
        self.yaw_velocity = 0

    def drone_stop(self):
        self.tello.send_rc_control(0, 0, 0, 0)

    def gesture_control(self, gesture_id):
        self._is_landing = False

        # RC control velocities
        self.forw_back_velocity = 0
        self.up_down_velocity = 0
        self.left_right_velocity = 0
        self.yaw_velocity = 0

        print("gesutrcontroller/GESTURE : ", gesture_id)
        if gesture_id is None:
            print("do nothing")
        else:
            if not self._is_landing:
                if gesture_id == 2:  # Forward
                    self.forw_back_velocity = 20
                elif gesture_id == 0:  # STOP
                    self.forw_back_velocity = self.up_down_velocity = \
                        self.left_right_velocity = self.yaw_velocity = 0
                if gesture_id == 1:  # Back
                    self.forw_back_velocity = -20

                elif gesture_id == 3:  # UP
                    self.up_down_velocity = 30
                elif gesture_id == 4:  # DOWN
                    self.up_down_velocity = -30

                elif gesture_id == 99:  # takeoff
                    self.forw_back_velocity = self.up_down_velocity = \
                        self.left_right_velocity = self.yaw_velocity = 0
                    self.tello.takeoff()
                elif gesture_id == 100:  # LAND
                    self._is_landing = True
                    self.forw_back_velocity = self.up_down_velocity = \
                        self.left_right_velocity = self.yaw_velocity = 0
                    self.tello.land()

                elif gesture_id == 6: # LEFT
                    self.left_right_velocity = 20
                elif gesture_id == 5: # RIGHT
                    self.left_right_velocity = -20

                elif gesture_id == 9: #rotate
                    self.yaw_velocity = 30
                elif gesture_id == 10: #rotate
                    self.yaw_velocity = -30

                elif gesture_id == -1:
                    self.forw_back_velocity = self.up_down_velocity = \
                        self.left_right_velocity = self.yaw_velocity = 0

                if gesture_id == 8:
                    self.tello.send_control_command("cw {}".format(360))
                elif gesture_id == 7:  #flip
                    self.tello.send_rc_control(0, 0, 0, 0)
                    self.tello.flip_right()
                else:
                    self.tello.send_rc_control(self.left_right_velocity, self.forw_back_velocity,
                                           self.up_down_velocity, self.yaw_velocity)


