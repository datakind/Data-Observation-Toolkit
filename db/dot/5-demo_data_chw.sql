
CREATE TABLE IF NOT EXISTS public.chw_chw(
    uuid UUID PRIMARY KEY,
    region VARCHAR(200) NULL
);
INSERT INTO public.chw_chw VALUES('7377ca1d9af5fafd1c2809abf6a71421', 'Region G');
INSERT INTO public.chw_chw VALUES('f3e483f9672231d737cf4fe38916e25a', 'Region D');
INSERT INTO public.chw_chw VALUES('b3b5128445a332dbf22d79a4447afb90', 'Region G');
INSERT INTO public.chw_chw VALUES('dae5d4daa47fe4a20768793d0d92ad38', 'Region D');
INSERT INTO public.chw_chw VALUES('f997b57e87e1d3ec538829433da11b54', 'Region A');
INSERT INTO public.chw_chw VALUES('13ca9b45f802f646afdf3fb56d5db76c', 'Region C');
INSERT INTO public.chw_chw VALUES('8361379a06c5edba7c310aa6805aacb3', 'Region E');
INSERT INTO public.chw_chw VALUES('c7765a6429319b7b759664bac4f35bc1', NULL);
INSERT INTO public.chw_chw VALUES('a24ac177a1477c354bac37ee2f9beddd', NULL);
INSERT INTO public.chw_chw VALUES('dad86815340e862417ef348f3236e918', NULL);

CREATE TABLE IF NOT EXISTS public.chw_patient(
    uuid UUID PRIMARY KEY,
    patient_uuid UUID NULL
);
INSERT INTO public.chw_patient VALUES('c6bedf149da20a29b491e8e658b1734a','bd83c0b08f2258d286f63b2f54e6e114');
INSERT INTO public.chw_patient VALUES('169c9610f113f36347548c810d2ce759','dac0997a77ccd9d284db5c70a3260481');
INSERT INTO public.chw_patient VALUES('08941ce8862ea37da3aa9e9f78dd15e7','434b4148ba480ffa79183f57fb70e605');
INSERT INTO public.chw_patient VALUES('aa28e323b644bf7d1e26acc867713f65','5c350c5496f95d76a15fcf416b1aad14');
INSERT INTO public.chw_patient VALUES('4dc07a6ad1723bc9331d5a2ddf9991d2','636027aad42d08afc26da9707b954636');
INSERT INTO public.chw_patient VALUES('02a4b717d02d98981be5284786032e2c','85fbb81b026d7e5d46889ace35ad97a1');
INSERT INTO public.chw_patient VALUES('d52e1f16367da47d37261954431e33fa','460b07267dd1c54d3a08cc59831b9b0b');
INSERT INTO public.chw_patient VALUES('2af4ec13aba15dd461fa7b8eef35887a','641a25faccb01f0f9f84e9fa422fbf06');
INSERT INTO public.chw_patient VALUES('5e6dbeb9a8172d4f743a6c81c30e2daf','c61f2145f8edf156e17c982c552b9b5d');
INSERT INTO public.chw_patient VALUES('b35f554d6b6a3976b63d62986fbc0dd5','4925f99436882b2ccd05e53d626b4150');
INSERT INTO public.chw_patient VALUES('0838e808efcdebaee57eab797421c486','0f11e8e33c971058d37c26b0f313d43a');
INSERT INTO public.chw_patient VALUES('f8df99f5f0c6cf2918d29efc442c7f2c','9be70ce66771ddb5cfd404baa489cd95');
INSERT INTO public.chw_patient VALUES('892fafb5536858ee33a97d73839bba82','9fb8038641f1f36f30b9e7405810e3a4');
INSERT INTO public.chw_patient VALUES('ec8f4d466f2d36f339b8c59c547d7d5c','41ea8cc88035089a9528329d52cbc03d');
INSERT INTO public.chw_patient VALUES('7eeff3fd75629df20073c37ffe5b4a91','e3b7e559d20d94459dc4015c971e9ba6');
INSERT INTO public.chw_patient VALUES('125bb691299995ad4a303d23a430525b','6cc4a2b686061bb80552c4aa639f9a2b');
INSERT INTO public.chw_patient VALUES('77042800303441f0303b9f2e4f2dfa7a','4d2fa4404563ce2dfa53219950625473');
INSERT INTO public.chw_patient VALUES('916c77d4ed83e9a8b6226aa89289fcf0','99f82af8508cb902abed43d92fb638cf');
INSERT INTO public.chw_patient VALUES('7b80ddd22c6ec15c30d654f286e6e9b6','700607ee0babe4a8ed92ef7b79ee1fcc');
INSERT INTO public.chw_patient VALUES('0cedad8ea32541e473d7c230b72674b8','5f67ff07bac28233e011216c9fc652d3');
INSERT INTO public.chw_patient VALUES('6bdb571e2f4ba63edda6f264a97afb37','01048140ed265eb1074eb5cbbdf28ad6');
INSERT INTO public.chw_patient VALUES('4ed321057ed42a7fc2f1b79eafa568e1','1ca1ab013d805d66fc8aa08e19b4e684');
INSERT INTO public.chw_patient VALUES('115ad88eddddfd05803462f354e34e8f','417d1b73579b86f5581c7543a77a1931');
INSERT INTO public.chw_patient VALUES('db0bf08715a8335aabb36f43785ee746','c84b1072da390e3987e0a995abfa1fee');
INSERT INTO public.chw_patient VALUES('969ae53d376e23c6bb92d5109dadf298','96ffc882e4dbbe73b5b6dc6be1e5846b');
INSERT INTO public.chw_patient VALUES('69e57b706e94ba13664a61b1c2bf78e1','1e8ea75513425d2ced4033bca1d47c6e');
INSERT INTO public.chw_patient VALUES('9e34a8b8d07988dcec7edcfee164ba39','533aaabb38a437996d5ca7eb0a58a5ec');
INSERT INTO public.chw_patient VALUES('6e314ec2bd67c8dc2a60a27faac96bc7','425d103efa50f0a172e200c33811614e');
INSERT INTO public.chw_patient VALUES('f1ffbe639867ce84c803a0c5086aa3b3','ab47f67735b1dd8a0ff6884dbd004a57');
INSERT INTO public.chw_patient VALUES('ddc0005db5f379c576b5e305a092016a','7b651a1eb9775196152d1a1e7b96f0ff');
INSERT INTO public.chw_patient VALUES('bf779f5d29730b37db63141d1afb44c7','4530b5a8732709abd9d7cce4aaff595c');
INSERT INTO public.chw_patient VALUES('81ae571deaa6b9a581e544f0381ea87e','2191618edd6a8d940ab2df3bec96addc');
INSERT INTO public.chw_patient VALUES('c95070414c90d5ce0ea257fa4f176c6e','594e46b040d87c077ce322b03f381aa7');
INSERT INTO public.chw_patient VALUES('ec52527cb58d62a0ced2cba1195d34e5','31d1bcb01ec7d25e550c2c531c3f0940');
INSERT INTO public.chw_patient VALUES('2a09842e838284c656dc015f91f5a61d','2bf2ea396a280ac401650f68e2d017ba');
INSERT INTO public.chw_patient VALUES('2e4d0501dac65f64dd4ca66904a1b20c','95bcdb4c0e11b963fad0be173f875d32');
INSERT INTO public.chw_patient VALUES('1ea782ca8adb5fe9cb38a781448222f5','e6b918b5a752307454266cf2a71056b6');
INSERT INTO public.chw_patient VALUES('94e4be876cc3f34056eb03acf10da781','0ccc9f01f30d9e476fee7a788319e056');
INSERT INTO public.chw_patient VALUES('3a9ee5dd27f72fa17a08a1ef0a487d52','01fcd5112b73ee64dbefe3cd91b340bf');
INSERT INTO public.chw_patient VALUES('69ec7efb15f0b526cf7770f455e0517d','4650ca592f5d04e018f3e723aeea2d90');
INSERT INTO public.chw_patient VALUES('e497ecab17cceedfef27f438b53e1f19','ba9b9ce21420c2b8a3f46b2e174227af');
INSERT INTO public.chw_patient VALUES('d3923b84fb4f460a8770036c09ecd5c9','8e7deae42d15c360253bdfe5c6273052');
INSERT INTO public.chw_patient VALUES('d233b55fddf017f91bd958387006d419','37837495f145936379d75c14e9c9cee9');
INSERT INTO public.chw_patient VALUES('02e51312df476846f8e1a47295afd86f','58e7efc1882249b48ba687e989888644');
INSERT INTO public.chw_patient VALUES('08e2290a6272bd35b05542b4ea4b3f5a','ad27b4d2c5e4235ef5ca22f99d2e969b');
INSERT INTO public.chw_patient VALUES('64e6e94942c1e0d4900154ad5b6921bc','9b6948581d60bda3b3ef956ef30cd5c5');
INSERT INTO public.chw_patient VALUES('3dbb8fa65b63a6a1a310a17918ea75dc','491f17a039379f20a90b6db3ee6dce2e');
INSERT INTO public.chw_patient VALUES('f546d5455b1ba1c41d925b4679031da0','1f4c125fb95ec912fca0ef20b29e32db');
INSERT INTO public.chw_patient VALUES('e0a692e5550f2e5c87b2440f9a8c799f','491f17a039379f20a90b6db3ee6dce2e');
INSERT INTO public.chw_patient VALUES('f11b67f7665b168bfd66dad9e263d600','1f4c125fb95ec912fca0ef20b29e32db');

CREATE TABLE IF NOT EXISTS public.chw_patient_assessment(
    uuid UUID PRIMARY KEY, 
    date DATE NULL,
    chw_id VARCHAR(200) NULL,
    patient_uuid VARCHAR(200) NULL,
    patient_temperature DOUBLE PRECISION NULL,
    danger_signs BOOLEAN NULL,
    malaria_test_result BOOLEAN NULL,
    malaria_treatment_given BOOLEAN NULL
);
INSERT INTO public.chw_patient_assessment VALUES('1e158cad80643cb26b5fc4baea773037','2004-03-26','dae5d4daa47fe4a20768793d0d92ad38','01fcd5112b73ee64dbefe3cd91b340bf','36.17','True','True','True');
INSERT INTO public.chw_patient_assessment VALUES('30168078d01e24c9a01ed43e5932d11f','2000-09-25','dae5d4daa47fe4a20768793d0d92ad38','9be70ce66771ddb5cfd404baa489cd95','36.23','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('e3143ea75c0532a42d3fa77af1e7e51a','2014-06-25','dad86815340e862417ef348f3236e918','460b07267dd1c54d3a08cc59831b9b0b','36.29','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('4cef821a25adfedfc2c2a3df5296ea77','2014-11-02','b3b5128445a332dbf22d79a4447afb90','5c350c5496f95d76a15fcf416b1aad14','35.49','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('9890a2f9dc0732d06070ecd8a62a5fba','2006-10-13','f997b57e87e1d3ec538829433da11b54','417d1b73579b86f5581c7543a77a1931','36.99','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('81fae000a526cf5709775b18b701e68d','2001-12-22','b3b5128445a332dbf22d79a4447afb90','0f11e8e33c971058d37c26b0f313d43a','35.49','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('3521e7e19f96e874c739b6aded62822d','2016-01-18','8361379a06c5edba7c310aa6805aacb3','e6b918b5a752307454266cf2a71056b6','36.7','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('112491055d9c75d8d68d4aa48cab0602','2008-07-15','b3b5128445a332dbf22d79a4447afb90','95bcdb4c0e11b963fad0be173f875d32','35.49','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('ffd2d9644cb2f54d96c11114b01fbba8','2018-07-09','f997b57e87e1d3ec538829433da11b54','c61f2145f8edf156e17c982c552b9b5d','36.58','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('f538848eda29341cfe532d2b1442ab75','2021-07-24','dad86815340e862417ef348f3236e918','c61f2145f8edf156e17c982c552b9b5d','36.82','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('4216632c7db48f4bcb086cb390b66abc','2020-03-25','dae5d4daa47fe4a20768793d0d92ad38','ad27b4d2c5e4235ef5ca22f99d2e969b','36.25','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('cfe1c473d0d1f8384f74e7da71527d0e','2019-05-01','8361379a06c5edba7c310aa6805aacb3','434b4148ba480ffa79183f57fb70e605','36.78','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('ed70c0b583c21d63b3ffe855ba7ab685','2005-05-13','c7765a6429319b7b759664bac4f35bc1','31d1bcb01ec7d25e550c2c531c3f0940','36.52','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('67b22109c2586a48e08129b2e841ede8','2015-11-20','7377ca1d9af5fafd1c2809abf6a71421','533aaabb38a437996d5ca7eb0a58a5ec','36.21','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('5661b01f421b642f3c9c801890eb06ae','2014-03-16','13ca9b45f802f646afdf3fb56d5db76c','bd83c0b08f2258d286f63b2f54e6e114','36.38','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('ba3dcc1b0eec3f61acdbf3a66c69bbed','2022-02-02','dae5d4daa47fe4a20768793d0d92ad38','5f67ff07bac28233e011216c9fc652d3','36.13','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('a2615b640bd3ffe77d09ff8a59b490ff','2000-09-28','f997b57e87e1d3ec538829433da11b54','ab47f67735b1dd8a0ff6884dbd004a57','36.45','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('a3460fdb5ca4b19d7b47f971d94350ab','2022-02-21','13ca9b45f802f646afdf3fb56d5db76c','641a25faccb01f0f9f84e9fa422fbf06','36.87','False','True','True');
INSERT INTO public.chw_patient_assessment VALUES('3d071ff9a6657622166432ce4ddb72e4','2008-11-01','a24ac177a1477c354bac37ee2f9beddd','01048140ed265eb1074eb5cbbdf28ad6','36.89','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('7dd78dd56bf409b42c47b85a02f08f08','2015-08-10','8361379a06c5edba7c310aa6805aacb3','c84b1072da390e3987e0a995abfa1fee','36.22','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('89e70067f1082ab13b630517c727191f','2004-09-16','b3b5128445a332dbf22d79a4447afb90','99f82af8508cb902abed43d92fb638cf','35.49','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('82a0f8bb2fdebbcb4790e6ffb27ef37a','2021-02-10','7377ca1d9af5fafd1c2809abf6a71421','434b4148ba480ffa79183f57fb70e605','36.2','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('678a748542d8631be841b1b38be9b2b4','2018-08-30','b3b5128445a332dbf22d79a4447afb90','700607ee0babe4a8ed92ef7b79ee1fcc','35.49','False','True','True');
INSERT INTO public.chw_patient_assessment VALUES('1e326190c0c32b5f9b8f0a9757ca73c4','2017-10-18','f3e483f9672231d737cf4fe38916e25a','5f67ff07bac28233e011216c9fc652d3','36.5','True','True','True');
INSERT INTO public.chw_patient_assessment VALUES('b0fef34122430fff343faae6d4b8034e','2016-05-15','c7765a6429319b7b759664bac4f35bc1','1ca1ab013d805d66fc8aa08e19b4e684','36.84','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('4d8470e5c24ef6b47684c744364bc6c5','2001-04-15','f997b57e87e1d3ec538829433da11b54','1ca1ab013d805d66fc8aa08e19b4e684','36.18','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('245c53cbd61219f5df3eb30d91c099be','2002-11-18','dae5d4daa47fe4a20768793d0d92ad38','1f4c125fb95ec912fca0ef20b29e32db','36.63','False','True','True');
INSERT INTO public.chw_patient_assessment VALUES('cc965822af7d0beea319c142b8017103','2017-08-28','f997b57e87e1d3ec538829433da11b54','ab47f67735b1dd8a0ff6884dbd004a57','36.57','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('73240581e6f3c74732fd7ba9d7bf275b','2008-11-16','dad86815340e862417ef348f3236e918','2746e1709b59a1c44c725d6d6d1cd759','36.2','True','True','True');
INSERT INTO public.chw_patient_assessment VALUES('368b364926325a1f4438995e94f6caa8','2000-12-09','a24ac177a1477c354bac37ee2f9beddd','ab47f67735b1dd8a0ff6884dbd004a57','36.87','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('59e89b749c5f59c31c709ac76f078a10','2001-06-07','dae5d4daa47fe4a20768793d0d92ad38','4650ca592f5d04e018f3e723aeea2d90','36.2','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('d871c56306ee62865ec1c48725d8a1f8','2005-02-23','f3e483f9672231d737cf4fe38916e25a','01fcd5112b73ee64dbefe3cd91b340bf','36.76','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('5f12c7d08c07be67405b42fbc62d4dc0','2017-09-25','c7765a6429319b7b759664bac4f35bc1','58e7efc1882249b48ba687e989888644','36.52','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('5a4501f970ed4ce2b7f0aa6f83e2403f','2007-06-11','7377ca1d9af5fafd1c2809abf6a71421','1ca1ab013d805d66fc8aa08e19b4e684','36.36','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('1e218a5ff74d7a1cee950826a252ac57','2008-09-27','dad86815340e862417ef348f3236e918','4925f99436882b2ccd05e53d626b4150','36.79','False','True','True');
INSERT INTO public.chw_patient_assessment VALUES('fc65e7e75ebbc161041c346e0fb23014','2001-05-04','f3e483f9672231d737cf4fe38916e25a','e3b7e559d20d94459dc4015c971e9ba6','36.31','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('f159fc92216dda7d46218983b56e2038','2011-04-01','b3b5128445a332dbf22d79a4447afb90','4925f99436882b2ccd05e53d626b4150','35.49','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('1156570233e7f3b9fbbe70a5fac5d804','2019-07-11','f3e483f9672231d737cf4fe38916e25a','58e7efc1882249b48ba687e989888644','36.75','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('4bceb6d8f0139bebe3f11e96fa16009d','2020-05-14','8361379a06c5edba7c310aa6805aacb3','4530b5a8732709abd9d7cce4aaff595c','36.38','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('270f641050bfe4bb1ff20533cd27f52b','2008-08-28','13ca9b45f802f646afdf3fb56d5db76c','636027aad42d08afc26da9707b954636','36.41','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('2634a6e7234f98f7dba57829ba493a43','2002-02-12','b3b5128445a332dbf22d79a4447afb90','8e7deae42d15c360253bdfe5c6273052','35.49','True','True','True');
INSERT INTO public.chw_patient_assessment VALUES('22309b5a3e9d982bba9aafd0e1e68529','2016-05-17','8361379a06c5edba7c310aa6805aacb3','4925f99436882b2ccd05e53d626b4150','36.9','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('738318ca72387d632647876748312485','2020-10-24','c7765a6429319b7b759664bac4f35bc1','96ffc882e4dbbe73b5b6dc6be1e5846b','36.14','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('b2ef545b40b6ce4abc4905cc5116b63b','2001-02-07','dad86815340e862417ef348f3236e918','4650ca592f5d04e018f3e723aeea2d90','36.11','True','False','False');
INSERT INTO public.chw_patient_assessment VALUES('ced801cefd7f085948a506e9c37fbb67','2016-09-06','f3e483f9672231d737cf4fe38916e25a','5c350c5496f95d76a15fcf416b1aad14','36.83','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('b68740914bb6fb2f0f2ce5feec3377af','2010-01-31','b3b5128445a332dbf22d79a4447afb90','96ffc882e4dbbe73b5b6dc6be1e5846b','35.49','False','True','True');
INSERT INTO public.chw_patient_assessment VALUES('c9298dadf9524b916c86b4ef35ba3c8f','2015-02-16','13ca9b45f802f646afdf3fb56d5db76c','ad1c299ec8e1ba27f681be882700d3f4','36.58','False','True','True');
INSERT INTO public.chw_patient_assessment VALUES('b9a182088f47957967d95615716eae42','2001-05-11','c7765a6429319b7b759664bac4f35bc1','4d2fa4404563ce2dfa53219950625473','36.3','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('51fefa8649ac7ef934e5a7994dfcd44d','2021-05-07','a24ac177a1477c354bac37ee2f9beddd','ad27b4d2c5e4235ef5ca22f99d2e969b','36.54','True','True','True');
INSERT INTO public.chw_patient_assessment VALUES('e6f058ee91a7afdc6399c311b3bef96d','2019-04-05','8361379a06c5edba7c310aa6805aacb3','85fbb81b026d7e5d46889ace35ad97a1','36.8','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('5fce366f3f322079e5708b1fde1e8e32','2020-11-07','c7765a6429319b7b759664bac4f35bc1','96ffc882e4dbbe73b5b6dc6be1e5846b','36.14','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('59d1936ac0522a8cef8bfda936d88c68','2001-02-21','dad86815340e862417ef348f3236e918','4650ca592f5d04e018f3e723aeea2d90','36.11','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('297887165f78e76b5b682a77b04a27f1','2021-05-21','a24ac177a1477c354bac37ee2f9beddd','ad27b4d2c5e4235ef5ca22f99d2e969b','36.54','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('b710a2fd70ecfa33dabdcf817a291fa0','2010-02-14','b3b5128445a332dbf22d79a4447afb90','96ffc882e4dbbe73b5b6dc6be1e5846b','35.49','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('959b99eba76d9f113954ce243565b27c','2015-03-02','13ca9b45f802f646afdf3fb56d5db76c','ad1c299ec8e1ba27f681be882700d3f4','36.58','False','False','False');
INSERT INTO public.chw_patient_assessment VALUES('fb094c9030ed0bdfc481972eefbde54c','2021-05-21','a24ac177a1477c354bac37ee2f9beddd','ad27b4d2c5e4235ef5ca22f99d2e969b','36.54','False','False','False');
