-- views in database
-- this table on which the table was built
-- virtual key

create view used_cars as 
select * from car where mileage > 50000;

drop view used_cars;

select * from used_cars;

create view popular_car_1 as
select car.

--can read, edit tables
--only one base table

-- materialized

--code done so far

create user ivan with password 'ivan1';
create user sophie with password 'sophie1';
create user kirill with password 'kirill1';

grant planadmin to ivan;
grant planmanager to sophie;
grant planmanager to kirill;

grant select on all tables in schema public to planadmin;
grant select on all tables in schema public to planmanager;

grant select, update, insert, delete on plan_data to planadmin;
grant select, update, insert, delete on plan_data to planmanager;

grant select, update, insert, delete on plan_status to planadmin;
grant select, update on plan_status to planmanager;

grant select, update, insert, delete on country_managers to planadmin;
grant select on country_managers to planmanager;

grant select, update on v_plan_edit to planmanager;

grant select on v_plan to planmanager;

insert into country_managers (username, country) values ('sophie', 'US');
insert into country_managers (username, country) values ('sophie', 'CA');

insert into country_managers (username, country) values ('kirill', 'FR');
insert into country_managers (username, country) values ('kirill', 'GB');
insert into country_managers (username, country) values ('kirill', 'DE');
insert into country_managers (username, country) values ('kirill', 'AU');

create materialized view product2 as
select p3.productcategoryid as pcid, p1.productid as productid, 
p3.name as pcname, p1.name as pname
from product p1 join productsubcategory p2 using (productsubcategoryid)
join productcategory p3 using(productcategoryid);

create materialized view country2 as
select distinct ad.countryregioncode 
from customer as c 
join customeraddress ca using(customerid)
join address ad using(addressid)
where ca.addresstype = 'Main Office';

--permission to managers and administrators
grant select on product2 to planadmin;
grant select on country2 to planadmin;
grant select on product2 to planmanager;
grant select on country2 to planmanager;

delete from customeraddress where addressid in (825, 1098);

insert into company (cname, countrycode, city)
select distinct c.companyname as cname, ad.countryregioncode, ad.city 
from customer c join customeraddress ca using(customerid)
join address ad using(addressid)
where ca.addresstype = 'Main Office';

select * from company c;
delete from company_abc;
insert into company_abc (cid, salestotal, cls, year)
select cid, sale_company as salestotal, case when srt <= sa then 'A' when srt <= sb then 'B' else 'C' end as cls,
year
from (select *, sum(ratings.sale_company)over(partition by year order by year desc rows between unbounded preceding and current row) as SRT
from 
(select c.id as cid, sum(sales.subtotal) as sale_company,extract(year from sales.orderdate) as year
from salesorderheader sales
join customer cus using(customerid)
join company c on cus.companyname = c.cname
where extract(year from sales.orderdate) = 2012 or extract (year from sales.orderdate) = 2013
group by c.id, extract(year from sales.orderdate) 
order by year desc, sale_company desc
)ratings
join 
(select sum(salestotal.subtotal) as totalsales, extract(year from salestotal.orderdate) as year, 
sum(salestotal.subtotal)*0.8 as sa, sum(salestotal.subtotal)*0.95 sb
from salesorderheader salestotal
join customer cus using (customerid)
join company c on cus.companyname = c.cname 
where extract(year from salestotal.orderdate) = 2012 or extract(year from salestotal.orderdate) = 2013
group by extract(year from salestotal.orderdate)
order by extract(year from salestotal.orderdate) desc) total using (year))total order by cid;

delete from company_sales;
insert into company_sales (cid, salesamt, year, quarter_yr, qr, categoryid, ccls)
select c.id as tid, sum(sd.linetotal) as salesamount, extract(year from sh.orderdate) as year,
extract(quarter from sh.orderdate) as quarter_yr,
to_char(sh.orderdate ::date, 'YYYY.Q') as qr, p2.pcid as categoryid, c_abc.cls
from salesorderdetail sd
join salesorderheader sh using(salesorderid)
join customer cu using (customerid)
join company c on cu.companyname = c.cname 
join product2 p2 using(productid)
join company_abc c_abc on c_abc.cid = c.id and c_abc.year = extract(year from sh.orderdate)
where extract(year from sh.orderdate) = 2012 or extract(year from sh.orderdate) = 2013
group by c.id, extract(year from sh.orderdate), extract(quarter from sh.orderdate), 
qr, categoryid, c_abc.cls;

select distinct c.countrycode country, cs.categoryid pcid,
sum(cs.salesamt)over(partition by quarter_yr, year, c.countrycode, cs.categoryid)/2 salesamt, quarter_yr, year 
from company_sales cs join company c on c.id = cs.cid where cs.ccls = 'A' or cs.ccls = 'B' order by country, pcid;

select 'N', countryregioncode as country, productcategoryid as pcid , coalesce(salesamt ,0) as salesamt 
from country2 cross join productcategory p
left join 
(select c.countrycode country, categoryid pcid, sum(salesamt)/2 as salesamt 
from company_sales cs
left join company as c on cs.cid = c.id 
left join country_managers cm on cm.country  = c.countrycode 
where quarter_yr = '1' and ccls != 'C' and year < '2014'
group by c.countrycode , categoryid
order by c.countrycode , categoryid) as t on t.country = countryregioncode and t.pcid = productcategoryid
order by countryregioncode, productcategoryid;

select * from company_abc where year = '2013' order by cls desc, salestotal desc;