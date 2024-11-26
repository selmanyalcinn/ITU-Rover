#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from pynput import keyboard
import threading

# Global değişkenler
twist = Twist()
active = True  # Robotun aktif olup olmadığını kontrol eder
lock = threading.Lock()

# Hareket fonksiyonları
def move_forward():
    with lock:
        twist.linear.x = 0.5
        twist.angular.z = 0.0

def move_backward():
    with lock:
        twist.linear.x = -0.5
        twist.angular.z = 0.0

def turn_left():
    with lock:
        twist.linear.x = 0.0
        twist.angular.z = 0.5

def turn_right():
    with lock:
        twist.linear.x = 0.0
        twist.angular.z = -0.5

def stop_movement():
    with lock:
        twist.linear.x = 0.0
        twist.angular.z = 0.0

# Klavye girdilerini işleyen fonksiyonlar
def on_press(key):
    try:
        if key.char == 'w':  # İleri
            move_forward()
            rospy.loginfo("İleri gidiliyor...")
        elif key.char == 's':  # Geri
            move_backward()
            rospy.loginfo("Geri gidiliyor...")
        elif key.char == 'a':  # Sola
            turn_left()
            rospy.loginfo("Sola dönülüyor...")
        elif key.char == 'd':  # Sağa
            turn_right()
            rospy.loginfo("Sağa dönülüyor...")
    except AttributeError:
        pass

def on_release(key):
    stop_movement()
    if key == keyboard.Key.esc:  # ESC ile çıkış
        return False

# 60 saniyelik zamanlayıcı
def timer():
    global active
    rospy.sleep(60)  # 60 saniye bekle
    active = False   # Robotu durdur
    rospy.loginfo("60 saniye doldu. Node kapatılıyor.")

if __name__ == '__main__':
    # ROS node'u başlat
    rospy.init_node('keyboard_control_timer')

    # Publisher oluştur
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(10)  # 10 Hz

    # Zamanlayıcıyı bir thread olarak başlat
    threading.Thread(target=timer).start()

    # Klavye dinleyicisini başlat
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while not rospy.is_shutdown() and active:
            with lock:
                pub.publish(twist)  # Hareket komutlarını yayımla
            rate.sleep()
        listener.stop()  # Dinleyiciyi durdur
    rospy.loginfo("Node kapatıldı.")
