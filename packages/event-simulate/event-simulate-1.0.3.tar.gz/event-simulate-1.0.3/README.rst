ģ������: event - ����ʹ��import userevent !

.. image:: https://tiebapic.baidu.com/forum/pic/item/4e4a20a4462309f707621658650e0cf3d7cad66f.jpg
    :alt: Build passing
.. image:: https://tiebapic.baidu.com/forum/pic/item/d1a20cf431adcbefc104ee4cbbaf2edda3cc9f4c.jpg
    :alt: 100% test coverage

���
====

event-simulate��һ��ģ�����,����¼���Python��, ����ģ����굥����˫��, ���̰��µȸ��ֲ���,

�����ڱ�д�Զ������� (����Ϸ���)��


������ģ�� Included modules: 
============================

event.key - ģ������¼�
""""""""""""""""""""""""
�����ĺ��� Functions:

keydown(keycode_or_keyname)::

    ģ������¡�
    keycode_or_keyname:�������ƻ�ð����ļ���ֵ

keypress(keycode_or_keyname, delay=0.05)::

    ģ�ⰴ����
    keycode_or_keyname:�������ƻ�ð����ļ���ֵ
    delay:���������ͷ�֮��ĵļ��ʱ��,���ʱ��ԽС,�����ٶ�Խ�졣

keyup(keycode_or_keyname)::

    ģ����ͷš�
    keycode_or_keyname:�������ƻ�ð����ļ���ֵ


event.mouse - ģ������¼�
""""""""""""""""""""""""""
�����ĺ��� Functions:

click()::

    ģ������������

dblclick(delay=0.25)::

    ģ��������˫��

get_screensize()::

    ��ȡ��ǰ��Ļ�ֱ��ʡ�

getpos()::

    ��ȡ��ǰ���λ�á�
    ����ֵΪһ��Ԫ��,��(x,y)��ʽ��ʾ��

move(x, y)::

    ģ���ƶ���ꡣ
    ��goto��ͬ,move()*����*һ������¼���

right_click()::

    ģ������Ҽ�������

ʾ������1:
.. code-block:: python

    #ģ�ⰴ��Alt+F4�رյ�ǰ����
    from event.key import *
    keydown("Alt")
    keydown("f4")
    keyup("f4")
    keyup("alt")

ʾ������2:
.. code-block:: python

    #ʹ��Aero PeekԤ�����档(Win7������ϵͳ)
    from event import mouse
    x,y=mouse.get_screensize()
    mouse.move(x,y) #�����������Ļ���½�
    mouse.click() #ģ�������


��������: 

������ʾ��:��������(��Ŀ¼\examples\mouseController.py)

�޸��˵���API����ʱ����``ValueError``��bug��


���� Author:

*�߷ֳ��� qq:3076711200 �ٶ��˺�:�쵤34*

����:3416445406@qq.com