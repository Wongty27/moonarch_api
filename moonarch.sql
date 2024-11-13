PGDMP  3                
    |            moonarch    16.3    16.3 /    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    57830    moonarch    DATABASE     }   CREATE DATABASE moonarch WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_Malaysia.932';
    DROP DATABASE moonarch;
                postgres    false            �            1259    66035 	   feedbacks    TABLE     �   CREATE TABLE public.feedbacks (
    order_id uuid NOT NULL,
    rating integer NOT NULL,
    platform character varying(255) NOT NULL,
    CONSTRAINT feedbacks_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);
    DROP TABLE public.feedbacks;
       public         heap    postgres    false            �            1259    57854    order_details    TABLE     �   CREATE TABLE public.order_details (
    order_id uuid NOT NULL,
    order_time timestamp without time zone NOT NULL,
    order_status character varying(50) NOT NULL,
    user_id uuid NOT NULL
);
 !   DROP TABLE public.order_details;
       public         heap    postgres    false            �            1259    57864    order_items    TABLE     �   CREATE TABLE public.order_items (
    order_id uuid NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL
);
    DROP TABLE public.order_items;
       public         heap    postgres    false            �            1259    74229    prebuilt    TABLE       CREATE TABLE public.prebuilt (
    build_id integer NOT NULL,
    build_name character varying(255) NOT NULL,
    build_parts jsonb,
    build_img_url character varying(255),
    build_cost numeric(10,2),
    build_price numeric(10,2),
    build_stock_count integer
);
    DROP TABLE public.prebuilt;
       public         heap    postgres    false            �            1259    74228    prebuilt_build_id_seq    SEQUENCE     �   CREATE SEQUENCE public.prebuilt_build_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.prebuilt_build_id_seq;
       public          postgres    false    224            �           0    0    prebuilt_build_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.prebuilt_build_id_seq OWNED BY public.prebuilt.build_id;
          public          postgres    false    223            �            1259    82467    prebuilt_order_items    TABLE     �   CREATE TABLE public.prebuilt_order_items (
    order_id uuid NOT NULL,
    build_id integer NOT NULL,
    quantity integer NOT NULL
);
 (   DROP TABLE public.prebuilt_order_items;
       public         heap    postgres    false            �            1259    57832    products    TABLE     8  CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_name character varying(255) NOT NULL,
    brand character varying(100) NOT NULL,
    category character varying(100) NOT NULL,
    cost numeric(10,2) NOT NULL,
    sales_price numeric(10,2) NOT NULL,
    stock_count integer NOT NULL
);
    DROP TABLE public.products;
       public         heap    postgres    false            �            1259    57831    products_product_id_seq    SEQUENCE     �   CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.products_product_id_seq;
       public          postgres    false    216            �           0    0    products_product_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;
          public          postgres    false    215            �            1259    57848    traffics    TABLE     �   CREATE TABLE public.traffics (
    traffic_id integer NOT NULL,
    visit_date date NOT NULL,
    number_of_visits integer NOT NULL
);
    DROP TABLE public.traffics;
       public         heap    postgres    false            �            1259    57847    traffics_traffic_id_seq    SEQUENCE     �   CREATE SEQUENCE public.traffics_traffic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.traffics_traffic_id_seq;
       public          postgres    false    219            �           0    0    traffics_traffic_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.traffics_traffic_id_seq OWNED BY public.traffics.traffic_id;
          public          postgres    false    218            �            1259    57838    users    TABLE     F  CREATE TABLE public.users (
    user_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    full_name character varying(255),
    phone_number character varying(20),
    address text,
    user_type character varying(50) DEFAULT 'customer'::character varying NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false            ;           2604    74232    prebuilt build_id    DEFAULT     v   ALTER TABLE ONLY public.prebuilt ALTER COLUMN build_id SET DEFAULT nextval('public.prebuilt_build_id_seq'::regclass);
 @   ALTER TABLE public.prebuilt ALTER COLUMN build_id DROP DEFAULT;
       public          postgres    false    223    224    224            8           2604    57835    products product_id    DEFAULT     z   ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);
 B   ALTER TABLE public.products ALTER COLUMN product_id DROP DEFAULT;
       public          postgres    false    216    215    216            :           2604    57851    traffics traffic_id    DEFAULT     z   ALTER TABLE ONLY public.traffics ALTER COLUMN traffic_id SET DEFAULT nextval('public.traffics_traffic_id_seq'::regclass);
 B   ALTER TABLE public.traffics ALTER COLUMN traffic_id DROP DEFAULT;
       public          postgres    false    219    218    219            �          0    66035 	   feedbacks 
   TABLE DATA           ?   COPY public.feedbacks (order_id, rating, platform) FROM stdin;
    public          postgres    false    222   �9       �          0    57854    order_details 
   TABLE DATA           T   COPY public.order_details (order_id, order_time, order_status, user_id) FROM stdin;
    public          postgres    false    220   );       �          0    57864    order_items 
   TABLE DATA           E   COPY public.order_items (order_id, product_id, quantity) FROM stdin;
    public          postgres    false    221   =       �          0    74229    prebuilt 
   TABLE DATA           �   COPY public.prebuilt (build_id, build_name, build_parts, build_img_url, build_cost, build_price, build_stock_count) FROM stdin;
    public          postgres    false    224   N?       �          0    82467    prebuilt_order_items 
   TABLE DATA           L   COPY public.prebuilt_order_items (order_id, build_id, quantity) FROM stdin;
    public          postgres    false    225   �L       �          0    57832    products 
   TABLE DATA           m   COPY public.products (product_id, product_name, brand, category, cost, sales_price, stock_count) FROM stdin;
    public          postgres    false    216   �L       �          0    57848    traffics 
   TABLE DATA           L   COPY public.traffics (traffic_id, visit_date, number_of_visits) FROM stdin;
    public          postgres    false    219   �_       �          0    57838    users 
   TABLE DATA           f   COPY public.users (user_id, email, password, full_name, phone_number, address, user_type) FROM stdin;
    public          postgres    false    217   r`       �           0    0    prebuilt_build_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.prebuilt_build_id_seq', 1, false);
          public          postgres    false    223            �           0    0    products_product_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.products_product_id_seq', 400, true);
          public          postgres    false    215            �           0    0    traffics_traffic_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.traffics_traffic_id_seq', 1, false);
          public          postgres    false    218            J           2606    66040    feedbacks feedbacks_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_pkey PRIMARY KEY (order_id);
 B   ALTER TABLE ONLY public.feedbacks DROP CONSTRAINT feedbacks_pkey;
       public            postgres    false    222            F           2606    57858     order_details order_details_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT order_details_pkey PRIMARY KEY (order_id);
 J   ALTER TABLE ONLY public.order_details DROP CONSTRAINT order_details_pkey;
       public            postgres    false    220            H           2606    57868    order_items order_items_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_id, product_id);
 F   ALTER TABLE ONLY public.order_items DROP CONSTRAINT order_items_pkey;
       public            postgres    false    221    221            N           2606    82471 .   prebuilt_order_items prebuilt_order_items_pkey 
   CONSTRAINT     |   ALTER TABLE ONLY public.prebuilt_order_items
    ADD CONSTRAINT prebuilt_order_items_pkey PRIMARY KEY (order_id, build_id);
 X   ALTER TABLE ONLY public.prebuilt_order_items DROP CONSTRAINT prebuilt_order_items_pkey;
       public            postgres    false    225    225            L           2606    74236    prebuilt prebuilt_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.prebuilt
    ADD CONSTRAINT prebuilt_pkey PRIMARY KEY (build_id);
 @   ALTER TABLE ONLY public.prebuilt DROP CONSTRAINT prebuilt_pkey;
       public            postgres    false    224            >           2606    57837    products products_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);
 @   ALTER TABLE ONLY public.products DROP CONSTRAINT products_pkey;
       public            postgres    false    216            D           2606    57853    traffics traffics_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.traffics
    ADD CONSTRAINT traffics_pkey PRIMARY KEY (traffic_id);
 @   ALTER TABLE ONLY public.traffics DROP CONSTRAINT traffics_pkey;
       public            postgres    false    219            @           2606    57846    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public            postgres    false    217            B           2606    57844    users users_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    217            R           2606    66041 !   feedbacks feedbacks_order_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.order_details(order_id) ON DELETE CASCADE;
 K   ALTER TABLE ONLY public.feedbacks DROP CONSTRAINT feedbacks_order_id_fkey;
       public          postgres    false    4678    222    220            O           2606    57859 (   order_details order_details_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT order_details_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 R   ALTER TABLE ONLY public.order_details DROP CONSTRAINT order_details_user_id_fkey;
       public          postgres    false    4674    217    220            P           2606    57869 %   order_items order_items_order_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.order_details(order_id) ON DELETE CASCADE;
 O   ALTER TABLE ONLY public.order_items DROP CONSTRAINT order_items_order_id_fkey;
       public          postgres    false    4678    221    220            Q           2606    57874 '   order_items order_items_product_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;
 Q   ALTER TABLE ONLY public.order_items DROP CONSTRAINT order_items_product_id_fkey;
       public          postgres    false    221    216    4670            S           2606    82477 7   prebuilt_order_items prebuilt_order_items_build_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.prebuilt_order_items
    ADD CONSTRAINT prebuilt_order_items_build_id_fkey FOREIGN KEY (build_id) REFERENCES public.prebuilt(build_id) ON DELETE CASCADE;
 a   ALTER TABLE ONLY public.prebuilt_order_items DROP CONSTRAINT prebuilt_order_items_build_id_fkey;
       public          postgres    false    4684    225    224            T           2606    82472 7   prebuilt_order_items prebuilt_order_items_order_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.prebuilt_order_items
    ADD CONSTRAINT prebuilt_order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.order_details(order_id) ON DELETE CASCADE;
 a   ALTER TABLE ONLY public.prebuilt_order_items DROP CONSTRAINT prebuilt_order_items_order_id_fkey;
       public          postgres    false    4678    220    225            �   2  x�U�=Nf1E����;��$z$��qF��}L1)��:����E*1� K�]�S>������q}X��7jѩ�j`+̚�4����������,8ٴ ��<v��� �O�|ɒ�������6���zL�UD����Z�D�2W��M��^�,!�IQ"yv�Q���Ǡ>ii=��������v�E$��Y[su/��?����v���}1(9�V�@���S�����#p�Ct��}X�����ߍ"d�[N�#�weAVO��>	ɇ�T��k�iUa��6#}|ǟ_�����y�_韀e      �   �  x���;�1�S�h�'����p"JTd�|��X�qblC�%t�����A�굼�vضm͘)��Y�֝���z���ǯ��;������rԍa��ŉ.���7۝�E!�8avK�#m���>9��D��p��3G"�^$0�&4-�h�mm����2�Ad�\������������BAvTHa�GB���!<�n�S�	a���q:�x�4���zr珞�p̷k���p�nϵc��7]=z΀M�(	�qb�lAsp�}>���z��l��j��K��4ݻ/��U0#�Ң��j��BAl�!}�v~r�����ON����ד�u�!<Jo�F������E���L���!n�|�k�Nm�r����<��.�LvɬS�ݱ8}+��E:#&�x���Q�����n+�J�rK���k��tē���}�߾�n�?@#      �   =  x���ˑ�*�uw.�%�@R.�1����pz�o��S2B+묔E����tz�$�X1��l��#�?�W!��# 5�S���R4U��R)�:���R���-D��q��lzzlR]�f�i�[
S�S��`�L3��L5���!p�m��e��iw�\N�e�G�_���Χ[Sm_���S�Q�7!F�U^,=��=����٘���۩,���O�����ȷ 5���4�Y(UtT�jxjt85���G�Ϡ�"�X7U�"i��G{֝-�8��	�P�&L�}���¨�몽ô��3g���_�g_�j�HcVit��TS������:�	�;[��0U�V�Ӏ[��ݳ^�}N�A��"�T�t�<ӂǶ����RI�Z�i��U(��`*	S�i����z����L��ild�sR���Y}����I�QQ�N�-�w� �����}c�nB��M����Z���I=�о�R���ͣ�[q��QU8����fC�
\�w'W@���^0�&�1������p�C�yRt�5d��8��S��b���B�rC��яQ/85��[�����5�      �   C  x���]W�8���_�훽�m��sΞ=&�K>���t��q'�h	v�v�a��ߒ��Ht�+�4[��޷���Τ,��Z�Q�T$��JI��v�����>����DW��t��OE�D���!�/+����66��'��mE���\�������\n�t�Ҭ	�+��PZ�t#��ă�斘�ņ�y�@�(�7��Z��2^��z�:.d��$��.�ʗ�U���_Ʊ�lk�i,�����sZ��v��d�7��=��XoOS�O�B�Z�puSh��^�%��s�g���,3�]�����-�Ѫݒ��y���j�푖yM����i%���F��nk�"x��_�LYnH�-d:�]�M�h8��!��J��+=�"շN�{53�ֻ�e��Z��1D�����<���v�ܟ�u�l�_?���) �������qa|���9����mW���'�,õM��-�꘮�^8f�r,�����i��U���dk r  [���Ցd��æ!ƙ�>(&i��pO#�@�<�H��Q~1-B���sY����8��@ɐ��g�$
!�������~���/7e� 149Z6N�9��jn�����O-l�R�i�1T��kPH��M�C���B��7 dۇ�@�+��>*�/mn2���^`�Bt�b!�s9��v��`π� �kA1�.v���KGIU�pb�p�����N
 'p���u����Òn���eS��%� M�7eu��94LoR4�E(V:V|[�
���n�.7;��L��%����ȮfsZ�HL5e"&.����()A,i����{�xy��<����$�p6�ǋHa����T�?����X��	���`?��Ϯ��mGI�74ȫG4/��,Ԑ��l��x�'�x2D��kLz��a�ln\-7�゠ ���6�t���b���
�A�mhY���(�q�'+�cj�q����Ri�T-���A�B��`[-5���̓ްD����"XÍ����p��.�$i�9�m�=���1�W��͢!&7w������.��x<FYEۓ��p4�*���)��_
�=]b��\����<7�@���>���%AQ�uH�|���o����Ij���3�|���f�j;.]��%�T�G���hq2]�Ȳ����!��9�vU>4����
;��Oxr���n˓�eh��O�M�G}	"S�o��{J��W�Wz�j���:��|]E 	o��$��X�,�M���&Kc�D?�7-tK�G�̏�nc��tO�2&�0���
H��o�u��+mQ"pe�\W�#$�g�w\C�hDZEc�Lx�y�d�@(y��V��2�]$�w.�1�C��9�˼�Kԯ�S�z$�y��$=�tNΖ�/���0E9S��ǂdQ&a����Rdj,�WQ���Xɶ��",쥸2u��/�V�����ulJ���I�0����t�1ͿUL�X���m�<��:f�dW�>KM$��BJ^Zǟe�$���N�v/>�І��MS٪��49�TJ��<)K���tLô.l���R����?2�o�_贉�G�$I6Pu-�G�&����P)�þc�$Ze_&�R^����w;�g34L�~O<em�$���v�d�
�%�gY�t�_�`6��Eo�(|O���B;��x y�a�,m9�B��0~Ӳa8�泛2�e#,��N�L�1K��h�9j�͖��@�����#���Ã���(brLH��PQE><!�E��@�Ƴ:���;qV���ǐI�\Y*	='�� 8
$�_�N�&L�e���t���l:(���j�5J�HE�!0$���w��c;[vx��%�e��|�ECU.��!�a�H�8��At�B��o^��df��Ml��9���u���5�>�'������x���fc�ɿ�f��xv{ Z�����a.�	|nٺ�����k;�>6�eB� �g[,H�����_ ��l�9��&��v%�,�*	�Z6x��.]�D�8�j���rZ��-FmK�|RӤ�"�?޻3-�9�7���K�R��/�:���+�KZ���9�^X;dE�^�Q����"a��b�C�NHu_VO���\9:���%�i�¤"+�˪�5X�0n?�r��Qc��:Z:(�Dׯ�<�`H���"y`FL�c9 ]L��.�G��;ٔP���F�u	��@H�)K�mk$I�7�$)�fx����V8(�>�P1��:,Ѐ>P�Q�Y���<?��o�����6Dp�(r��G	a�L7tY�V�"�ݽ/F��m�:������i�H�G8�%��dv4�Q��N�9�#ԟ͇��?7� ��?�,�aǓ�cs�}�;��sy�A�f�8pn�,��G^���U��h���H�ylHd	�dW�얬�:_��-y턺��#kz�����P�v�����<�mw��m.L��Tvt���Q�����V�M�#e#���i,��_k�A	������~��8ǖ��@f�u�ө�w���Bw���>�*G����B��ls��x�/���C��\�����(���P�CEt����`:׼�@�<� ���/@��`#$����J���D�6���0�)T�c�n
�F�8��nMC���6K��s�b
J7��H�E<�YY��M"#8� G�A�
Â�1zf�<���S`ɑXҨ�+4"3�9��/�Q�ۏ_��@�]��Ķn��Uul3����|x;Sk�"���|�������ɹ2>�~X���$�
�3d�=��A��X��Y��r��9�u9g_�������3�Ԛ�Xkn�v=G<ٚEܦ�	��Mt5
�b�Jm�ak��[Sn�͇P�߅��G����L�k.�����B���p� y9�S@�/gq$��W�.�͆�}~��@Ӌӻ�ĲCEkA;t�7H*���b]t�'B�(����]�QE���lq�Q��Qn���6�_�k�%����%I7;2}# )3r���;O�H&�X�7� �����$T��œ�G��r��}�0c�EH�s�m9���VP�����2��;�v�_��11={� �0%m��>��C�B��$M�%�Ա��Fe���@���Iw�N(��zIӇ�Ą��05�L�'�	�D�k0�/hV�N��������&���eJ���C掏�6����A8�F�I<�k:��  }
L�����cw9�'L��ʊU�[B���l�*�e.�|��냎؍TSeb��.��`��Вv��1¤�B|��̦�#)�qt��ʩ�d�9B%L����0}�G�a��ܓ]�~��@��L�5�K��,�o%؆�����UF�\�D��[�Ҽ�_{�!�*��s��⎃}��1:N� ��ߋn����\t      �   N   x�ʱ� �Zv!�Ga�4q���o�A�4VC�����QցBxJ���>W8�8�����$/��1ţ����ED�4�      �      x��ZIw�<�]3���cbത5YmM%ʶ��Ffbvd�MI_����} ���j�.�7��(�s/=��=M"�g���μ�����b�"/NI�E�������9K�u񜟫ھ0��hp/��L�����ߥ,���֗�`�������U<���}�UVް�E���?��lQ�^�/~�%`V}�˚)������[���Az�"�Bo�׿&����:��/�hG4�a�zÐ�y�:ߟ����m��.����1���m_�����S|�b�JZ*�ov|*������<��R&�{҈�G_���:��Wl���ړ	�,���s��޼̏l^��l�~�_�=?���)�A�<�]p'.r�.��՜	�Q/���Mz��=��i��lYT쟗�E�ݐ��BN\y�����e����X4�v�p8���`r�o�-�8��̃��"������_r,�����C�S���O�kk����\H¨x�����Sc�}P��|��$I!����WQ��ձ`�|-ꜭ���@#x1HD�2}��۾�k~8�
�X��yg�a0����i��"��}��PP&���T�q��-8D':o��G�rd����[�l�D�b��qx��{�qy��Ë�u��K]�z�f;�Y�c� ������z��KĐg6���o,5��%��ë`� ��Qu��5�T�_� ��J���KH���r��d��l;f�ᨍ-)B>�'VA��(�h���!��<���@Jk	 �7�g�l�Ƈ�\����f3��kwAO�4J�舱7�S�ٙn��o/�Ѭ���A�^��b�膼u���o��b2_=�ֻ΀����:a-K�y�4?�/��֊�z��� 1ϪE��$�ٌ-�S6\m �>�F,#,�;��p[a#�)�����KΖw7#ri��1B�	0x����p�#�E�:�=%=�\��Z��}	KCd�K-�wGn����(5�����痂M.�9���x��6�@�2��x�H'�U��R�9#I8qԸ�$�D������@Qԇ�tb�锟NH�ם�΢��r+��J��:�ٰzE\x���|�PёL~pY�H�;2����D\���+���u&`�Mh�:Vm�s��b�6�C�	���������Ny �A�6W {4�LZ	ڔ�dgzĢ��/a (`t�� �/��\Цg	PAgz���;]D� ���ag���.��|{�~�$� y�L�+T�B^�d��UD(��U�|���=[��M�$�jTGƯ��dRE+Y� DH�����'($�R�0rU�UHj3x�&	zY&7�߿7/�:���g\�������� QEqg���a`�>'��$�3�@}���N:+�
�;mA#��W���+�-\�@��( =�Ic�!](��$!tw��츃�\dGX����@"�F�&�	�hr}<q�"��B���;"�]�F�̐T$}�֐w���?*1A��f�Qc:�;�"�\��ӂ��m� �T��f�H�mY����t�,,iˤ�.�@�F)����z$��"�*��W�OV�
�:p������p]�(��I�Q�s@Eچ�@�D� a��ɐw��^?!V"TCҡ�iq �ʠ�Cn�L>H|{� �������8iy��BA�EG��f��|��,͖t$S��]"�9��Dm��p,ل�+�ۑ-fIQV�j6jy��&�����h&��^������d\���� ԩ���2D#oH����gأ`]�6�G1��'!��B�KY�.#=ZJ�T�D����+""�~�Х(,A�Ź�U|�VX4�$wN]���V�O�Q5�Hv]�����n�.{Y_D�HВ4���t�n��>lV��=7f��I�1��y��f�C���l�݌c��f���f�7�%� 5�hH�!F8�h�Քe��l���.�� �&N˱��l[��H�2�r�P��a¦��� �Ύ�┽�o3$l%��p���+��k��yY��/��qs��7Y�Y�zӼ<���g���zm�یt��ۓkQE�4��;�M;(zc *1�i.K�A��M�ۯ����i�%�h��ͽ�tb
	�G|/N�9V^�ag��Sƣ��4<�r�䈕×�p`;��͈�2�O%��r���$?�V�(mRe��M�P��Q�E��T���,d��JC
O�jPNщ��Ƹ:L|��Q���4�=�7�۵bv�$��Y������q6��lR](�����<#ݵ'�̡%�������X#����k
yO��*#�օ��\��6� h�\쭗_�n��[-=�7[�����fGÍq(�gΦ�܉��~�v�)�٨��<t�v�6�����줏*�:��Feۺ<���v=j� ��3�#I��"���̟���wu��{<��6#��h�I��7��D��@o�����]�����m�(�����T'���'���$�=�q$�+�~���}�+��:��U�^�'GW0���C�Bo[�^��H�/�M � a��fi`$ ����V���Ffn�{Ķ��t���ޢ����v"U� msV/�����~;f]�]70�ͨ��}��`��Qt��ĘŽ�����l4dw� ����{�A}4�P��M�-k�wH�>X�pj|Y*.#�Q�?��gI�df�Ӿ1(���(�Xx$> �hNFu^�J�,%�SA��Ț}����\ˎX#������S?a�U6�=@}(Mq)a��3`����.O��]!,Q�\šQ_k4n5%�����#�Qq��ŽL�ki�wE0g]�pW�ŝ�?���1��p��3�"�m:���ZZ��@���e� �	uF���Z����
~�*j^�,�Ϩ>&���"T@a��٠E갚Un��Ge�D?[og��gxj�!Y5E?�]�o�����m^�_>=�B��rm:�"��E��-i܍7+C�z���F�����m�7������*[��KDf	J�c�"�7�'@F�\6�"�Ԏ�x���Z�n��D�"Sۍ�c:�������=������������n����S4�J����X�#��ǥۢ���w����2]��%%P���45Z��{v�ֳ�~��U�!��N"=;FGw��F7��]ҵ��T�U�5�*t�O� ��F	�\@�c4]i��������"�͞��jTj4��g�ޥO��<�
F'��B��ŭ?��[@6�&v�6��i6�}�	8	\[��S�.#4j��/\�#q�����#l#��z��y�wm�0��ֵ%NK���3�w�55�����u��H��-����cW�l4�������:]Z��Z��qY���!��^�s����De��R�ןm[��!?��˫k���a��}rU�٪�n�Yā��7�bH�7n�*K�z�J�C�o�u�.qU:�}mD�Um����vi���X�SF8��&�k���!�-�����-�8Y��0����ճ��&�8X�W��U�aΡKH�l��ޟ���v����ޛ ��nDԔd�z�Ő�R�S��]o���;�FY1�\�al8-@���o`(�e ۆL�X����:2Z�:��-B��Su�������ѽ6v�b�M���8�����n`�}�u��!�'ʶ$���6�5s��@�eχ�~3(ۑ Y6���?�!�j48�_�_��g^��şV��So��B"t�^�\u���ϗ7��t"�2�N�^%T���b�f�ꏆl3N�[�����΍��1���,�۔�~�0ް�h܄$)��f�ۤ�ݛ� ����Q�Z���ޟ�}f1�,ָ�^.
�.	�uA��-�X�q_��zG����*�&p�X5� 8�/����ٟ��X�2��X�VT�UR��bo�7�s�����
�&�g3ڨ�l�����Єr��t�ț���|N��3uɿ�f;�,O�R6i5��*�����'�x}���0i��$�x�b6G28�!:�;{�qk�����xO�}��\�wv�=�H3��"�E�-�`W�t�����L�׶"�͋? �  `~�f�]�B�����NӸDH���B����$/���F�B�`���D8\�W�TO?����i�nP��M�OA����.�3{,)n|�Cv��O_���6%#�}u�}�^=}���{޹�>L�m��b�Y=���w�;�
Ġ�Tꦺ�Eҥ:X��j���>?�o��_,җ�\ئn��`�M�Ǧ��yN��1g
�iw�F j����Z ��l7�^Ď[]K�����q7~�4X���"_7tL��2���n�>�˸�F�5���ঁ�M��.ވwŲoQ���E#���p��x�F.��� 腪a �(W��iqTzW'������y?��������T�U�	h^5;��E���ӗ�B��5A������B�F��Q�Neu�Ֆ��
ø��,��A��$qb���t;{X��������"��h���/��_�Qk75�͛B9QYy'�ʃ�Jڳ5�k��m�7�O�n�3ɕ���j�*:^NYy3˿��*�o��3SȻ�L��hF��UB����.ǟ,AAJ b�C��:k��xL8t;?t�M��䡦�����:0��J�����,�Z�QrM��������P���f;b�th,տI7�,����6�
��	]�!Iڦh���1��4r�$�J��g��̖d��١��DMd����/_� �,�      �   �   x�Eѻ�0К��9�Y�d�9B:wF'��(����Υ����#��

�y7����ް��[����lWch�8+���H)\�\�t��E8\���t��K�����-J0ACSPKK@���*di	di
j�������e)�,MA:d�#�,-� KK0�-MA~����S�      �   �  x�u��R�:���S������Œ�C ٷ���e�1�86���Gf�9éR�JR���w7��;Ji�) &J �JBj�<��[i]Tq���T�IC�u�k^'�G���Z��u�UZ��Fg��J&���ۆ�σ�|�y�����\U���s��P�*��+�.�vF.�H c���hGZ�ʳ�q�:�t����FZ���o��r߃�*��p�0�+�����'l���D��x����Nڃ�5�D�W"���� B�0&�B����կ�H�خ��c?���T��{�2�E7��HD}��e!Ä#�.��=	�2%À{[����*q(6wi����ET���<<�G��Dc6�S��jP�0y�vd����S�:g��=}*O���Ț����g�*p���Ÿ�3b3{��BT76s]Ǳ{�&/l_l
s�~��C䰀@1��J��'WY��b���M_@�t�ϭ`k�����`�E{��!��D'�̶��LM���v�����*kn�6/?` ��(e��0~��Kۏ���B.L�ʼك*�U��P*t$i0�p�@i�!ɕ����o��C�u@#�/|������D��a���h3/�n�Я���ׇ�ȟU7����:�V�՞�G��� a�Q�-�'T3�}�8��/M*�a�8$Trx �ƞ �@��%"��eZ�Ľ���0nf���K9��qS����~T����ZeGʖ�d��܇�m\/g���.�\�@�\�& ���<�BO{n�9�2
�*v!�[G��;����4}�������6FoVh�Y���{<O��L��7�q��F��B��B�25�	V�@�$4��UEC�Y�M����[o[�t�,:�c�|���D-vv��m���I�=y?ҽ��ְ*�f��?���2ۧ�O����?�$.2��w}��C��`�< ��@Bs
s�T�O�� 	׏�y�f�R?9�1lM��>�N��+o���9��|��ОD~��}�@�Cnq $��Hj,�8�@	 "�9��oY��ƛ�b_��)Cf������M��N7u�����r=��~�J�<S�%u.�Q3��aް!����f���M����=+b���wcctI�L���J�6�L�2F�����%��|i\]]��#�     