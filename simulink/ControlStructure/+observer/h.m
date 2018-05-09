function h = h(in1)
%H
%    H = H(IN1)

%    This function was generated by the Symbolic Math Toolbox version 8.0.
%    09-May-2018 14:06:08

eta1 = in1(1,:);
eta2 = in1(2,:);
eta3 = in1(3,:);
eta4 = in1(4,:);
eta5 = in1(5,:);
eta6 = in1(6,:);
l = in1(28,:);
l_t = in1(29,:);
p1 = in1(19,:);
p2 = in1(20,:);
p3 = in1(21,:);
p_t1 = in1(22,:);
p_t2 = in1(23,:);
p_t3 = in1(24,:);
phi1 = in1(30,:);
phi2 = in1(31,:);
v1 = in1(7,:);
v2 = in1(8,:);
v3 = in1(9,:);
v4 = in1(10,:);
v5 = in1(11,:);
v6 = in1(12,:);
t2 = sin(eta4);
t3 = sin(eta6);
t4 = cos(eta4);
t5 = cos(eta6);
t6 = sin(eta5);
t7 = p1.*8.676474650532034e-1;
t8 = p2.*4.971783612075956e-1;
t9 = p3.*1.246408311757266e-3;
t10 = t7+t8+t9+1.536041691521612;
t11 = p2.*3.690033198352161e-3;
t12 = p3.*9.99986887020921e-1;
t20 = p1.*3.550977499600688e-3;
t13 = t11+t12-t20+1.024461448780775;
t14 = cos(eta5);
t15 = p1.*4.971672424300975e-1;
t16 = p3.*4.967117124448933e-3;
t18 = p2.*8.676405135780166e-1;
t17 = t15+t16-t18+1.082024099747949;
t19 = cos(phi1);
h = [eta1;eta2;eta3;eta4;eta5;eta6;v1;v2;v3;v4;v5;v6;p1;p2;p3;p_t1;p_t2;p_t3;eta1-t10.*(t3.*t4-t2.*t5.*t6)-t13.*(t2.*t3+t4.*t5.*t6)-l.*sin(phi1)-t5.*t14.*t17;eta2+t10.*(t4.*t5+t2.*t3.*t6)+t13.*(t2.*t5-t3.*t4.*t6)+l.*t19.*sin(phi2)-t3.*t14.*t17;eta3+t6.*t17+l.*t19.*cos(phi2)+t2.*t10.*t14-t4.*t13.*t14;l;l_t];
