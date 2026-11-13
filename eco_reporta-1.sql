-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 09-11-2026 a las 01:31:25
-- Versión del servidor: 10.11.16-MariaDB
-- Versión de PHP: 8.5.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `eco_reporta`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `areas_plantel`
--

CREATE TABLE `areas_plantel` (
  `id_area` int(11) NOT NULL,
  `nombre_area` varchar(100) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `areas_plantel`
--

INSERT INTO `areas_plantel` (`id_area`, `nombre_area`, `descripcion`) VALUES
(1, 'Jardín Principal', 'Área verde delantera del plantel'),
(2, 'Cafetería', 'Zona de comedor y cocina'),
(3, 'Edificio A - Aulas', 'Salones de clase del primer piso');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estados_reporte`
--

CREATE TABLE `estados_reporte` (
  `id_estado` int(11) NOT NULL,
  `nombre_estado` varchar(50) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estados_reporte`
--

INSERT INTO `estados_reporte` (`id_estado`, `nombre_estado`, `descripcion`) VALUES
(1, 'Pendiente', 'El reporte fue recibido y aún no se ha atendido'),
(2, 'En proceso', 'El reporte está siendo atendido por el personal'),
(3, 'Resuelto', 'El problema reportado ya fue solucionado'),
(4, 'Cerrado', 'El reporte se da por finalizado y archivado'),
(5, 'Rechazado', 'El reporte no procede o es inválido');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_reparaciones`
--

CREATE TABLE `historial_reparaciones` (
  `id_reparacion` int(11) NOT NULL,
  `id_reporte` int(11) NOT NULL,
  `fecha_reparacion` datetime NOT NULL,
  `descripcion` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historial_reparaciones`
--

INSERT INTO `historial_reparaciones` (`id_reparacion`, `id_reporte`, `fecha_reparacion`, `descripcion`) VALUES
(1, 1, '2025-02-02 11:00:00', 'Se reemplazó la manguera dañada y se revisó la presión del agua'),
(2, 2, '2025-02-04 09:30:00', 'Cambio de foco LED y limpieza de la lámpara'),
(3, 3, '2025-02-06 14:15:00', 'Se soldó la pata de la silla y se reforzó la estructura');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `imagenes_reporte`
--

CREATE TABLE `imagenes_reporte` (
  `id_imagen` int(11) NOT NULL,
  `id_reporte` int(11) NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `ruta_archivo` varchar(500) NOT NULL COMMENT 'Ruta relativa o URL de la imagen',
  `fecha_subida` datetime NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `imagenes_reporte`
--

INSERT INTO `imagenes_reporte` (`id_imagen`, `id_reporte`, `nombre_archivo`, `ruta_archivo`, `fecha_subida`, `descripcion`) VALUES
(1, 1, 'fuga_jardin_01.jpg', './Imagenes/fuga_jardin_01.jpg', '2025-02-01 08:22:00', 'Foto de la manguera con fuga'),
(2, 2, 'lampara_cafeteria.jpg', './Imagenes/lampara_cafeteria.jpg', '2025-02-03 16:12:00', 'Lámpara fundida en zona de mesas'),
(3, 3, 'silla_rota_aula102.jpg', './Imagenes/silla_rota_aula102.jpg', '2025-02-05 10:48:00', 'Silla con pata rota en el aula 102');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prioridades_reporte`
--

CREATE TABLE `prioridades_reporte` (
  `id_prioridad` int(11) NOT NULL,
  `nombre_prioridad` varchar(50) NOT NULL,
  `nivel` int(11) NOT NULL COMMENT 'Número para ordenar (1=más baja, 3=más alta)',
  `descripcion` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `prioridades_reporte`
--

INSERT INTO `prioridades_reporte` (`id_prioridad`, `nombre_prioridad`, `nivel`, `descripcion`) VALUES
(1, 'Baja', 1, 'Problema menor que no afecta operaciones'),
(2, 'Media', 2, 'Problema que requiere atención en un plazo razonable'),
(3, 'Alta', 3, 'Problema importante que afecta el uso normal del área');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reportes_incidencias`
--

CREATE TABLE `reportes_incidencias` (
  `id_reporte` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_area` int(11) NOT NULL,
  `id_estado` int(11) NOT NULL DEFAULT 1,
  `id_prioridad` int(11) NOT NULL DEFAULT 2,
  `descripcion` varchar(250) NOT NULL,
  `fecha_reporte` datetime NOT NULL,
  `problema` varchar(100) NOT NULL,
  `fotografia` varchar(255) DEFAULT NULL,
  `prioridad` enum('Baja','Media','Alta') DEFAULT 'Baja',
  `motivo_ia` varchar(500) DEFAULT NULL,
  `estado` enum('Pendiente','En proceso','Resuelto') DEFAULT 'Pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `reportes_incidencias`
--

INSERT INTO `reportes_incidencias` (`id_reporte`, `id_usuario`, `id_area`, `id_estado`, `id_prioridad`, `descripcion`, `fecha_reporte`, `problema`, `fotografia`, `prioridad`, `motivo_ia`, `estado`) VALUES
(1, 1, 1, 3, 3, 'Fuga de agua en la manguera del jardín', '2025-02-01 08:20:00', '', NULL, 'Baja', NULL, 'Pendiente'),
(2, 2, 2, 3, 2, 'Lámpara fundida en la zona de mesas', '2025-02-03 16:10:00', '', NULL, 'Baja', NULL, 'Pendiente'),
(3, 3, 3, 3, 2, 'Silla rota en el aula 102', '2025-02-05 10:45:00', '', NULL, 'Baja', NULL, 'Pendiente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(150) NOT NULL,
  `fecha_registro` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre`, `correo`, `fecha_registro`) VALUES
(1, 'Ana López', 'ana.lopez@ejemplo.com', '2025-01-10 09:15:00'),
(2, 'Carlos Ramírez', 'carlos.ramirez@ejemplo.com', '2025-01-12 14:30:00'),
(3, 'María Fernández', 'maria.fernandez@ejemplo.com', '2025-01-15 11:45:00');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `areas_plantel`
--
ALTER TABLE `areas_plantel`
  ADD PRIMARY KEY (`id_area`);

--
-- Indices de la tabla `estados_reporte`
--
ALTER TABLE `estados_reporte`
  ADD PRIMARY KEY (`id_estado`);

--
-- Indices de la tabla `historial_reparaciones`
--
ALTER TABLE `historial_reparaciones`
  ADD PRIMARY KEY (`id_reparacion`),
  ADD KEY `id_reporte` (`id_reporte`);

--
-- Indices de la tabla `imagenes_reporte`
--
ALTER TABLE `imagenes_reporte`
  ADD PRIMARY KEY (`id_imagen`),
  ADD KEY `id_reporte` (`id_reporte`);

--
-- Indices de la tabla `prioridades_reporte`
--
ALTER TABLE `prioridades_reporte`
  ADD PRIMARY KEY (`id_prioridad`);

--
-- Indices de la tabla `reportes_incidencias`
--
ALTER TABLE `reportes_incidencias`
  ADD PRIMARY KEY (`id_reporte`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_area` (`id_area`),
  ADD KEY `id_estado` (`id_estado`),
  ADD KEY `id_prioridad` (`id_prioridad`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `areas_plantel`
--
ALTER TABLE `areas_plantel`
  MODIFY `id_area` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `estados_reporte`
--
ALTER TABLE `estados_reporte`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `historial_reparaciones`
--
ALTER TABLE `historial_reparaciones`
  MODIFY `id_reparacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `imagenes_reporte`
--
ALTER TABLE `imagenes_reporte`
  MODIFY `id_imagen` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `prioridades_reporte`
--
ALTER TABLE `prioridades_reporte`
  MODIFY `id_prioridad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `reportes_incidencias`
--
ALTER TABLE `reportes_incidencias`
  MODIFY `id_reporte` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `historial_reparaciones`
--
ALTER TABLE `historial_reparaciones`
  ADD CONSTRAINT `historial_reparaciones_ibfk_1` FOREIGN KEY (`id_reporte`) REFERENCES `reportes_incidencias` (`id_reporte`);

--
-- Filtros para la tabla `imagenes_reporte`
--
ALTER TABLE `imagenes_reporte`
  ADD CONSTRAINT `imagenes_reporte_ibfk_1` FOREIGN KEY (`id_reporte`) REFERENCES `reportes_incidencias` (`id_reporte`) ON DELETE CASCADE;

--
-- Filtros para la tabla `reportes_incidencias`
--
ALTER TABLE `reportes_incidencias`
  ADD CONSTRAINT `reportes_incidencias_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  ADD CONSTRAINT `reportes_incidencias_ibfk_2` FOREIGN KEY (`id_area`) REFERENCES `areas_plantel` (`id_area`),
  ADD CONSTRAINT `reportes_incidencias_ibfk_3` FOREIGN KEY (`id_estado`) REFERENCES `estados_reporte` (`id_estado`),
  ADD CONSTRAINT `reportes_incidencias_ibfk_4` FOREIGN KEY (`id_prioridad`) REFERENCES `prioridades_reporte` (`id_prioridad`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
